from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from models import Document, DocumentVersion, DocumentControlValidation, DocumentType, User, SOAControl, SOAVersion, db
from datetime import datetime, date
from werkzeug.utils import secure_filename
from dateutil.relativedelta import relativedelta
import os
import mimetypes
import subprocess
import tempfile
from services.ai_verification import AIVerificationService

documents_bp = Blueprint('documents', __name__)

# Configuración de archivos permitidos
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp', 'txt', 'md'}
UPLOAD_FOLDER = 'uploads/documents'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_next_version_number(document):
    """Calcula el siguiente número de versión"""
    if not document.version:
        return '1.0'

    try:
        major, minor = document.version.split('.')
        minor = int(minor) + 1
        return f"{major}.{minor}"
    except:
        return '1.1'

def convert_office_to_pdf(file_path):
    """
    Convierte un documento Office (DOCX, XLSX, PPTX) a PDF usando LibreOffice.
    Retorna la ruta del archivo PDF temporal generado, o None si falla.
    """
    # Verificar que el archivo existe
    if not os.path.exists(file_path):
        return None

    # Verificar que es un archivo Office
    ext = file_path.lower().split('.')[-1]
    if ext not in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'odt', 'ods', 'odp']:
        return None

    try:
        # Crear directorio temporal para el PDF
        temp_dir = tempfile.mkdtemp()

        # Ejecutar LibreOffice en modo headless para convertir a PDF
        # --headless: modo sin interfaz gráfica
        # --convert-to pdf: formato de salida
        # --outdir: directorio de salida
        result = subprocess.run([
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', temp_dir,
            file_path
        ], capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            print(f"Error al convertir documento: {result.stderr}")
            return None

        # Obtener el nombre del archivo PDF generado
        original_filename = os.path.basename(file_path)
        pdf_filename = os.path.splitext(original_filename)[0] + '.pdf'
        pdf_path = os.path.join(temp_dir, pdf_filename)

        # Verificar que el PDF se creó
        if os.path.exists(pdf_path):
            return pdf_path
        else:
            return None

    except subprocess.TimeoutExpired:
        print("Timeout al convertir documento a PDF")
        return None
    except Exception as e:
        print(f"Error al convertir documento: {str(e)}")
        return None

def update_control_maturity(control_ids):
    """Actualiza la madurez de los controles a nivel 2 (Repetible) cuando se documenta"""
    for control_id in control_ids:
        control = SOAControl.query.get(control_id)
        if control:
            # Solo actualizar si el nivel actual es menor a 2
            current_maturity_scores = {
                'no_implementado': 0,
                'inicial': 1,
                'repetible': 2,
                'definido': 3,
                'controlado': 4,
                'cuantificado': 5,
                'optimizado': 6
            }

            current_score = current_maturity_scores.get(control.maturity_level, 0)
            if current_score < 2:
                control.maturity_level = 'repetible'
                control.implementation_status = 'implemented'

@documents_bp.route('/')
@login_required
def index():
    """Lista todos los documentos con filtros"""
    # Obtener parámetros de filtro
    doc_type = request.args.get('type')
    status = request.args.get('status')
    search = request.args.get('search')

    # Query base
    query = Document.query

    # Aplicar filtros
    if doc_type:
        # Buscar el tipo de documento por código
        dt = DocumentType.query.filter_by(code=doc_type).first()
        if dt:
            query = query.filter_by(document_type_id=dt.id)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            db.or_(
                Document.title.ilike(f'%{search}%'),
                Document.content.ilike(f'%{search}%')
            )
        )

    documents = query.order_by(Document.updated_at.desc()).all()

    # Estadísticas
    stats = {
        'total': Document.query.count(),
        'draft': Document.query.filter_by(status='draft').count(),
        'review': Document.query.filter_by(status='review').count(),
        'approved': Document.query.filter_by(status='approved').count(),
        'ai_verified': Document.query.filter_by(ai_verified=True).count(),
    }

    return render_template('documents/index.html',
                         documents=documents,
                         stats=stats,
                         current_type=doc_type,
                         current_status=status,
                         search_term=search)

@documents_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """Crea un nuevo documento"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para crear documentos', 'error')
        return redirect(url_for('documents.index'))

    if request.method == 'POST':
        try:
            # Obtener el tipo de documento por código
            doc_type_code = request.form['document_type']
            doc_type = DocumentType.query.filter_by(code=doc_type_code).first()
            if not doc_type:
                flash(f'Tipo de documento "{doc_type_code}" no válido', 'error')
                return redirect(url_for('documents.create'))

            # Crear documento base
            # Usar el autor especificado o el usuario actual si no se especifica
            author_id = request.form.get('author_id')
            if not author_id:
                author_id = current_user.id
            else:
                author_id = int(author_id)

            document = Document(
                title=request.form['title'],
                document_type_id=doc_type.id,
                content=request.form.get('content', ''),
                author_id=author_id,
                version='1.0'
            )

            # Manejar archivo subido
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"

                    # Crear directorio si no existe
                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)

                    document.file_path = filepath
                    document.file_size = os.path.getsize(filepath)
                    document.file_type = mimetypes.guess_type(filepath)[0]

            db.session.add(document)
            db.session.flush()  # Para obtener el ID

            # Crear primera versión
            first_version = DocumentVersion(
                document_id=document.id,
                version_number='1.0',
                file_path=document.file_path,
                file_size=document.file_size,
                file_type=document.file_type,
                content=document.content,
                status='draft',
                change_notes='Versión inicial',
                created_by_id=current_user.id
            )
            db.session.add(first_version)
            db.session.flush()

            document.current_version_id = first_version.id

            # Asociar controles SOA seleccionados
            control_ids = request.form.getlist('related_controls')
            if control_ids:
                controls = SOAControl.query.filter(SOAControl.id.in_(control_ids)).all()
                document.related_controls.extend(controls)

                # Actualizar madurez de controles
                update_control_maturity(control_ids)

            db.session.commit()

            flash('Documento creado correctamente', 'success')
            return redirect(url_for('documents.view', id=document.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el documento: {str(e)}', 'error')
            return redirect(url_for('documents.create'))

    # Obtener controles de la versión actual del SOA
    current_version = SOAVersion.get_current_version()
    controls = []
    if current_version:
        controls = SOAControl.query.filter_by(
            soa_version_id=current_version.id
        ).order_by(SOAControl.control_id).all()

    # Obtener tipos de documento activos
    document_types = DocumentType.query.filter_by(is_active=True).order_by(DocumentType.order).all()

    # Obtener lista de usuarios para el selector de autor
    users = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name, User.username).all()

    return render_template('documents/create.html', controls=controls, document_types=document_types, users=users)

@documents_bp.route('/<int:id>')
@login_required
def view(id):
    """Vista detallada de un documento"""
    document = Document.query.get_or_404(id)
    versions = document.versions.order_by(DocumentVersion.created_at.desc()).all()
    ai_validations = DocumentControlValidation.query.filter_by(
        document_id=id
    ).order_by(DocumentControlValidation.validated_at.desc()).all()

    return render_template('documents/view.html',
                         document=document,
                         versions=versions,
                         ai_validations=ai_validations)

@documents_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edita un documento creando una nueva versión"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para editar documentos', 'error')
        return redirect(url_for('documents.view', id=id))

    document = Document.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Obtener el tipo de documento por código
            doc_type_code = request.form['document_type']
            doc_type = DocumentType.query.filter_by(code=doc_type_code).first()
            if not doc_type:
                flash(f'Tipo de documento "{doc_type_code}" no válido', 'error')
                return redirect(url_for('documents.edit', id=id))

            # Actualizar información básica
            document.title = request.form['title']
            document.document_type_id = doc_type.id
            content = request.form.get('content', '')

            # Actualizar autor si se proporciona
            author_id = request.form.get('author_id')
            if author_id:
                document.author_id = int(author_id)

            # Obtener controles actuales antes de modificar
            old_control_ids = set([c.id for c in document.related_controls])

            # Verificar si hay cambios que requieran nueva versión
            content_changed = document.content != content
            file_changed = False

            new_file_path = document.file_path
            new_file_size = document.file_size
            new_file_type = document.file_type

            # Manejar nuevo archivo
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"

                    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)

                    new_file_path = filepath
                    new_file_size = os.path.getsize(filepath)
                    new_file_type = mimetypes.guess_type(filepath)[0]
                    file_changed = True

            # Si hay cambios significativos, crear nueva versión
            if content_changed or file_changed:
                new_version_number = get_next_version_number(document)

                new_version = DocumentVersion(
                    document_id=document.id,
                    version_number=new_version_number,
                    file_path=new_file_path,
                    file_size=new_file_size,
                    file_type=new_file_type,
                    content=content,
                    status='draft',
                    change_notes=request.form.get('change_notes', 'Actualización del documento'),
                    created_by_id=current_user.id
                )
                db.session.add(new_version)
                db.session.flush()

                document.current_version_id = new_version.id
                document.version = new_version_number
                document.file_path = new_file_path
                document.file_size = new_file_size
                document.file_type = new_file_type

                # Marcar para re-verificación IA si estaba verificado
                if document.ai_verified:
                    document.ai_needs_reverification = True

            document.content = content
            document.updated_at = datetime.utcnow()

            # Actualizar controles asociados
            new_control_ids = set(request.form.getlist('related_controls'))

            if old_control_ids != new_control_ids:
                document.related_controls = []
                if new_control_ids:
                    controls = SOAControl.query.filter(SOAControl.id.in_(new_control_ids)).all()
                    document.related_controls.extend(controls)

                    # Actualizar madurez de nuevos controles
                    added_controls = new_control_ids - old_control_ids
                    update_control_maturity(list(added_controls))

            db.session.commit()
            flash('Documento actualizado correctamente', 'success')
            return redirect(url_for('documents.view', id=document.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el documento: {str(e)}', 'error')

    # Obtener controles disponibles
    current_version = SOAVersion.get_current_version()
    controls = []
    if current_version:
        controls = SOAControl.query.filter_by(
            soa_version_id=current_version.id
        ).order_by(SOAControl.control_id).all()

    # Obtener tipos de documento activos
    document_types = DocumentType.query.filter_by(is_active=True).order_by(DocumentType.order).all()

    # Obtener lista de usuarios para el selector de autor
    users = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name, User.username).all()

    return render_template('documents/edit.html', document=document, controls=controls, document_types=document_types, users=users)

@documents_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Elimina un documento"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para eliminar documentos', 'error')
        return redirect(url_for('documents.view', id=id))

    document = Document.query.get_or_404(id)

    try:
        # Eliminar archivo físico si existe
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Romper la referencia circular antes de eliminar versiones
        document.current_version_id = None
        db.session.flush()

        # Eliminar archivos de versiones
        for version in document.versions:
            if version.file_path and os.path.exists(version.file_path):
                os.remove(version.file_path)
            db.session.delete(version)

        # Eliminar validaciones IA
        for validation in document.ai_validations:
            db.session.delete(validation)

        # El documento se desasocia de los controles automáticamente por la relación many-to-many
        db.session.delete(document)
        db.session.commit()

        flash('Documento eliminado correctamente', 'success')
        return redirect(url_for('documents.index'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el documento: {str(e)}', 'error')
        return redirect(url_for('documents.view', id=id))

@documents_bp.route('/<int:id>/download')
@login_required
def download(id):
    """Descarga el archivo del documento"""
    document = Document.query.get_or_404(id)

    if not document.file_path or not os.path.exists(document.file_path):
        flash('El documento no tiene archivo adjunto', 'error')
        return redirect(url_for('documents.view', id=id))

    return send_file(
        document.file_path,
        as_attachment=True,
        download_name=f"{document.title}_v{document.version}.{document.file_extension}"
    )

@documents_bp.route('/<int:id>/view-pdf')
@login_required
def view_as_pdf(id):
    """Convierte documentos Office a PDF para visualización en el navegador"""
    document = Document.query.get_or_404(id)

    if not document.file_path or not os.path.exists(document.file_path):
        flash('El documento no tiene archivo adjunto', 'error')
        return redirect(url_for('documents.view', id=id))

    # Convertir a PDF
    pdf_path = convert_office_to_pdf(document.file_path)

    if not pdf_path:
        flash('No se pudo convertir el documento a PDF', 'error')
        return redirect(url_for('documents.view', id=id))

    try:
        # Enviar el PDF temporal
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f"{document.title}_v{document.version}.pdf"
        )
    finally:
        # Limpiar el archivo temporal después de enviarlo
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            # Eliminar también el directorio temporal
            temp_dir = os.path.dirname(pdf_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
        except:
            pass

@documents_bp.route('/version/<int:id>/download')
@login_required
def download_version(id):
    """Descarga una versión específica del documento"""
    version = DocumentVersion.query.get_or_404(id)

    if not version.file_path or not os.path.exists(version.file_path):
        flash('Esta versión no tiene archivo adjunto', 'error')
        return redirect(url_for('documents.view', id=version.document_id))

    return send_file(
        version.file_path,
        as_attachment=True,
        download_name=f"{version.document.title}_v{version.version_number}.{version.file_path.rsplit('.', 1)[-1]}"
    )

@documents_bp.route('/<int:id>/change-status', methods=['POST'])
@login_required
def change_status(id):
    """Cambia el estado de un documento"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para cambiar el estado del documento', 'error')
        return redirect(url_for('documents.view', id=id))

    document = Document.query.get_or_404(id)
    new_status = request.form.get('status')

    allowed_statuses = ['draft', 'review', 'approved', 'obsolete']
    if new_status not in allowed_statuses:
        flash('Estado no válido', 'error')
        return redirect(url_for('documents.view', id=id))

    try:
        document.status = new_status

        if new_status == 'approved':
            document.approver_id = current_user.id
            document.approval_date = date.today()
            # Calcular próxima revisión (1 año desde aprobación)
            if not document.next_review_date:
                document.next_review_date = date.today() + relativedelta(years=1)

        db.session.commit()
        flash(f'Estado cambiado a {new_status}', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado: {str(e)}', 'error')

    return redirect(url_for('documents.view', id=id))

@documents_bp.route('/<int:id>/versions')
@login_required
def versions(id):
    """Muestra el historial de versiones de un documento"""
    document = Document.query.get_or_404(id)
    versions = document.versions.order_by(DocumentVersion.created_at.desc()).all()

    return render_template('documents/versions.html', document=document, versions=versions)

@documents_bp.route('/<int:id>/clone', methods=['POST'])
@login_required
def clone(id):
    """Clona un documento existente"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para clonar documentos', 'error')
        return redirect(url_for('documents.view', id=id))

    original = Document.query.get_or_404(id)

    try:
        # Crear clon
        cloned = Document(
            title=f"{original.title} (Copia)",
            document_type_id=original.document_type_id,
            content=original.content,
            author_id=current_user.id,
            version='1.0',
            parent_document_id=original.id
        )

        # Copiar archivo si existe
        if original.file_path and os.path.exists(original.file_path):
            ext = original.file_path.rsplit('.', 1)[-1]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{timestamp}_copia_{os.path.basename(original.file_path)}"
            new_filepath = os.path.join(UPLOAD_FOLDER, new_filename)

            import shutil
            shutil.copy2(original.file_path, new_filepath)

            cloned.file_path = new_filepath
            cloned.file_size = original.file_size
            cloned.file_type = original.file_type

        db.session.add(cloned)
        db.session.flush()

        # Crear primera versión del clon
        first_version = DocumentVersion(
            document_id=cloned.id,
            version_number='1.0',
            file_path=cloned.file_path,
            file_size=cloned.file_size,
            file_type=cloned.file_type,
            content=cloned.content,
            status='draft',
            change_notes='Documento clonado',
            created_by_id=current_user.id
        )
        db.session.add(first_version)
        db.session.flush()

        cloned.current_version_id = first_version.id

        # Copiar controles asociados
        cloned.related_controls.extend(original.related_controls)

        db.session.commit()
        flash('Documento clonado correctamente', 'success')
        return redirect(url_for('documents.edit', id=cloned.id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al clonar el documento: {str(e)}', 'error')
        return redirect(url_for('documents.view', id=id))

@documents_bp.route('/<int:id>/verify-ai', methods=['POST'])
@login_required
def verify_ai(id):
    """Verifica el documento usando IA contra los controles SOA relacionados"""
    if not current_user.can_access('documents'):
        return jsonify({'success': False, 'error': 'No tienes permisos para verificar documentos'}), 403

    document = Document.query.get_or_404(id)

    # Validaciones
    if not document.related_controls:
        return jsonify({'success': False, 'error': 'El documento no tiene controles SOA relacionados'}), 400

    if not document.has_file:
        return jsonify({'success': False, 'error': 'El documento no tiene archivo adjunto'}), 400

    try:
        # Inicializar servicio de verificación
        ai_service = AIVerificationService()

        # Verificar disponibilidad
        available, message = ai_service.is_available()
        if not available:
            return jsonify({'success': False, 'error': message}), 503

        # Realizar verificación
        results = ai_service.verify_document(document, document.related_controls)

        # Guardar resultados en la base de datos
        # Actualizar el documento
        document.ai_verified = True
        document.ai_verification_date = datetime.utcnow()
        document.ai_verification_version = document.version
        document.ai_model_used = results['model_used']
        document.ai_overall_score = results['overall_score']
        document.ai_verified_by_id = current_user.id
        document.ai_needs_reverification = False

        # Guardar validaciones individuales por control
        for validation_data in results['validations']:
            control_id = validation_data['control_id']

            # Buscar si ya existe una validación previa
            existing_validation = DocumentControlValidation.query.filter_by(
                document_id=document.id,
                control_id=control_id
            ).first()

            if existing_validation:
                # Actualizar existente
                existing_validation.document_version = document.version
                existing_validation.compliance_status = validation_data['compliance_status']
                existing_validation.confidence_level = validation_data['confidence_level']
                existing_validation.overall_score = validation_data['overall_score']
                existing_validation.summary = validation_data['summary']
                existing_validation.covered_aspects = validation_data['covered_aspects']
                existing_validation.missing_aspects = validation_data['missing_aspects']
                existing_validation.evidence_quotes = validation_data['evidence_quotes']
                existing_validation.recommendations = validation_data['recommendations']
                existing_validation.maturity_suggestion = validation_data['maturity_suggestion']
                existing_validation.ai_model = results['model_used']
                existing_validation.tokens_used = validation_data['tokens_used']
                existing_validation.validation_time = validation_data['validation_time']
                existing_validation.validated_at = datetime.utcnow()
                existing_validation.validated_by_id = current_user.id
            else:
                # Crear nueva
                new_validation = DocumentControlValidation(
                    document_id=document.id,
                    control_id=control_id,
                    document_version=document.version,
                    compliance_status=validation_data['compliance_status'],
                    confidence_level=validation_data['confidence_level'],
                    overall_score=validation_data['overall_score'],
                    summary=validation_data['summary'],
                    covered_aspects=validation_data['covered_aspects'],
                    missing_aspects=validation_data['missing_aspects'],
                    evidence_quotes=validation_data['evidence_quotes'],
                    recommendations=validation_data['recommendations'],
                    maturity_suggestion=validation_data['maturity_suggestion'],
                    ai_model=results['model_used'],
                    tokens_used=validation_data['tokens_used'],
                    validation_time=validation_data['validation_time'],
                    validated_at=datetime.utcnow(),
                    validated_by_id=current_user.id
                )
                db.session.add(new_validation)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Verificación completada exitosamente',
            'overall_score': results['overall_score'],
            'verified_controls': results['verified_controls'],
            'total_controls': results['total_controls']
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@documents_bp.route('/<int:id>/update-verification-comments', methods=['POST'])
@login_required
def update_verification_comments(id):
    """Actualiza los comentarios de verificación del documento"""
    if not current_user.can_access('documents'):
        return jsonify({'success': False, 'error': 'No tienes permisos para modificar documentos'}), 403

    document = Document.query.get_or_404(id)

    try:
        comments = request.json.get('comments', '')
        document.ai_verification_comments = comments
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Comentarios guardados correctamente'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
