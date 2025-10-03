from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, ISOVersion, DocumentType
from datetime import datetime

auxiliary_bp = Blueprint('auxiliary', __name__)

@auxiliary_bp.route('/iso-versions')
@login_required
def iso_versions():
    """Lista todas las versiones ISO disponibles"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('dashboard.index'))

    versions = ISOVersion.query.order_by(ISOVersion.year.desc()).all()
    return render_template('auxiliary/iso_versions.html', versions=versions)

@auxiliary_bp.route('/iso-versions/new', methods=['GET', 'POST'])
@login_required
def create_iso_version():
    """Crea una nueva versión ISO"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para crear versiones ISO', 'error')
        return redirect(url_for('auxiliary.iso_versions'))

    if request.method == 'POST':
        try:
            version = request.form.get('version')
            year = request.form.get('year')
            title = request.form.get('title')
            description = request.form.get('description')
            number_of_controls = request.form.get('number_of_controls')
            is_active = request.form.get('is_active') == 'on'

            # Validaciones
            if not version or not year or not title:
                flash('Los campos Versión, Año y Título son obligatorios', 'error')
                return render_template('auxiliary/iso_version_form.html', form_data=request.form)

            # Verificar que la versión no exista
            existing_version = ISOVersion.query.filter_by(version=version).first()
            if existing_version:
                flash(f'Ya existe una versión ISO con el código {version}', 'error')
                return render_template('auxiliary/iso_version_form.html', form_data=request.form)

            new_version = ISOVersion(
                version=version,
                year=int(year),
                title=title,
                description=description,
                number_of_controls=int(number_of_controls) if number_of_controls else None,
                is_active=is_active
            )

            db.session.add(new_version)
            db.session.commit()

            flash(f'Versión ISO {version} creada exitosamente', 'success')
            return redirect(url_for('auxiliary.iso_versions'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la versión ISO: {str(e)}', 'error')
            return render_template('auxiliary/iso_version_form.html', form_data=request.form)

    return render_template('auxiliary/iso_version_form.html', form_data=None)

@auxiliary_bp.route('/iso-versions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_iso_version(id):
    """Edita una versión ISO existente"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para editar versiones ISO', 'error')
        return redirect(url_for('auxiliary.iso_versions'))

    version = ISOVersion.query.get_or_404(id)

    if request.method == 'POST':
        try:
            version_code = request.form.get('version')
            year = request.form.get('year')
            title = request.form.get('title')
            description = request.form.get('description')
            number_of_controls = request.form.get('number_of_controls')
            is_active = request.form.get('is_active') == 'on'

            # Validaciones
            if not version_code or not year or not title:
                flash('Los campos Versión, Año y Título son obligatorios', 'error')
                return render_template('auxiliary/iso_version_form.html', version=version, form_data=request.form)

            # Verificar que la versión no exista (excepto la actual)
            existing_version = ISOVersion.query.filter_by(version=version_code).first()
            if existing_version and existing_version.id != id:
                flash(f'Ya existe una versión ISO con el código {version_code}', 'error')
                return render_template('auxiliary/iso_version_form.html', version=version, form_data=request.form)

            version.version = version_code
            version.year = int(year)
            version.title = title
            version.description = description
            version.number_of_controls = int(number_of_controls) if number_of_controls else None
            version.is_active = is_active
            version.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'Versión ISO {version_code} actualizada exitosamente', 'success')
            return redirect(url_for('auxiliary.iso_versions'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la versión ISO: {str(e)}', 'error')
            return render_template('auxiliary/iso_version_form.html', version=version, form_data=request.form)

    return render_template('auxiliary/iso_version_form.html', version=version, form_data=None)

@auxiliary_bp.route('/iso-versions/<int:id>/delete', methods=['POST'])
@login_required
def delete_iso_version(id):
    """Elimina una versión ISO"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para eliminar versiones ISO', 'error')
        return redirect(url_for('auxiliary.iso_versions'))

    version = ISOVersion.query.get_or_404(id)

    try:
        # TODO: Verificar si la versión está siendo usada en algún SOA
        # Si está en uso, no permitir eliminar

        db.session.delete(version)
        db.session.commit()

        flash(f'Versión ISO {version.version} eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la versión ISO: {str(e)}', 'error')

    return redirect(url_for('auxiliary.iso_versions'))

@auxiliary_bp.route('/iso-versions/<int:id>/toggle-active', methods=['POST'])
@login_required
def toggle_iso_version_active(id):
    """Activa o desactiva una versión ISO"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para modificar versiones ISO', 'error')
        return redirect(url_for('auxiliary.iso_versions'))

    version = ISOVersion.query.get_or_404(id)

    try:
        version.is_active = not version.is_active
        version.updated_at = datetime.utcnow()
        db.session.commit()

        status = 'activada' if version.is_active else 'desactivada'
        flash(f'Versión ISO {version.version} {status} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado de la versión ISO: {str(e)}', 'error')

    return redirect(url_for('auxiliary.iso_versions'))

# ============== TIPOS DE DOCUMENTOS ==============

@auxiliary_bp.route('/document-types')
@login_required
def document_types():
    """Lista todos los tipos de documentos disponibles"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('dashboard.index'))

    types = DocumentType.query.order_by(DocumentType.order).all()
    return render_template('auxiliary/document_types.html', types=types)

@auxiliary_bp.route('/document-types/new', methods=['GET', 'POST'])
@login_required
def create_document_type():
    """Crea un nuevo tipo de documento"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para crear tipos de documentos', 'error')
        return redirect(url_for('auxiliary.document_types'))

    if request.method == 'POST':
        try:
            code = request.form.get('code')
            name = request.form.get('name')
            description = request.form.get('description')
            review_period_months = request.form.get('review_period_months')
            requires_approval = request.form.get('requires_approval') == 'on'
            approval_workflow = request.form.get('approval_workflow')
            icon = request.form.get('icon')
            color = request.form.get('color')
            is_active = request.form.get('is_active') == 'on'
            order = request.form.get('order')

            # Validaciones
            if not code or not name:
                flash('Los campos Código y Nombre son obligatorios', 'error')
                return render_template('auxiliary/document_type_form.html', form_data=request.form)

            # Verificar que el código no exista
            existing_type = DocumentType.query.filter_by(code=code).first()
            if existing_type:
                flash(f'Ya existe un tipo de documento con el código {code}', 'error')
                return render_template('auxiliary/document_type_form.html', form_data=request.form)

            new_type = DocumentType(
                code=code,
                name=name,
                description=description,
                review_period_months=int(review_period_months) if review_period_months else 12,
                requires_approval=requires_approval,
                approval_workflow=approval_workflow,
                icon=icon or 'fa-file',
                color=color or 'primary',
                is_active=is_active,
                order=int(order) if order else 0
            )

            db.session.add(new_type)
            db.session.commit()

            flash(f'Tipo de documento {name} creado exitosamente', 'success')
            return redirect(url_for('auxiliary.document_types'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el tipo de documento: {str(e)}', 'error')
            return render_template('auxiliary/document_type_form.html', form_data=request.form)

    return render_template('auxiliary/document_type_form.html', form_data=None)

@auxiliary_bp.route('/document-types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document_type(id):
    """Edita un tipo de documento existente"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para editar tipos de documentos', 'error')
        return redirect(url_for('auxiliary.document_types'))

    doc_type = DocumentType.query.get_or_404(id)

    if request.method == 'POST':
        try:
            code = request.form.get('code')
            name = request.form.get('name')
            description = request.form.get('description')
            review_period_months = request.form.get('review_period_months')
            requires_approval = request.form.get('requires_approval') == 'on'
            approval_workflow = request.form.get('approval_workflow')
            icon = request.form.get('icon')
            color = request.form.get('color')
            is_active = request.form.get('is_active') == 'on'
            order = request.form.get('order')

            # Validaciones
            if not code or not name:
                flash('Los campos Código y Nombre son obligatorios', 'error')
                return render_template('auxiliary/document_type_form.html', doc_type=doc_type, form_data=request.form)

            # Verificar que el código no exista (excepto el actual)
            existing_type = DocumentType.query.filter_by(code=code).first()
            if existing_type and existing_type.id != id:
                flash(f'Ya existe un tipo de documento con el código {code}', 'error')
                return render_template('auxiliary/document_type_form.html', doc_type=doc_type, form_data=request.form)

            doc_type.code = code
            doc_type.name = name
            doc_type.description = description
            doc_type.review_period_months = int(review_period_months) if review_period_months else 12
            doc_type.requires_approval = requires_approval
            doc_type.approval_workflow = approval_workflow
            doc_type.icon = icon or 'fa-file'
            doc_type.color = color or 'primary'
            doc_type.is_active = is_active
            doc_type.order = int(order) if order else 0
            doc_type.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'Tipo de documento {name} actualizado exitosamente', 'success')
            return redirect(url_for('auxiliary.document_types'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el tipo de documento: {str(e)}', 'error')
            return render_template('auxiliary/document_type_form.html', doc_type=doc_type, form_data=request.form)

    return render_template('auxiliary/document_type_form.html', doc_type=doc_type, form_data=None)

@auxiliary_bp.route('/document-types/<int:id>/delete', methods=['POST'])
@login_required
def delete_document_type(id):
    """Elimina un tipo de documento"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para eliminar tipos de documentos', 'error')
        return redirect(url_for('auxiliary.document_types'))

    doc_type = DocumentType.query.get_or_404(id)

    try:
        # Verificar si el tipo está siendo usado en documentos
        if doc_type.documents:
            flash(f'No se puede eliminar el tipo de documento {doc_type.name} porque está siendo usado en {len(doc_type.documents)} documento(s)', 'error')
            return redirect(url_for('auxiliary.document_types'))

        db.session.delete(doc_type)
        db.session.commit()

        flash(f'Tipo de documento {doc_type.name} eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el tipo de documento: {str(e)}', 'error')

    return redirect(url_for('auxiliary.document_types'))

@auxiliary_bp.route('/document-types/<int:id>/toggle-active', methods=['POST'])
@login_required
def toggle_document_type_active(id):
    """Activa o desactiva un tipo de documento"""
    if not current_user.can_access('documents'):
        flash('No tienes permisos para modificar tipos de documentos', 'error')
        return redirect(url_for('auxiliary.document_types'))

    doc_type = DocumentType.query.get_or_404(id)

    try:
        doc_type.is_active = not doc_type.is_active
        doc_type.updated_at = datetime.utcnow()
        db.session.commit()

        status = 'activado' if doc_type.is_active else 'desactivado'
        flash(f'Tipo de documento {doc_type.name} {status} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado del tipo de documento: {str(e)}', 'error')

    return redirect(url_for('auxiliary.document_types'))
