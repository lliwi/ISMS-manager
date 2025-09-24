from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Document, User, SOAControl, SOAVersion, db
from datetime import datetime

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/')
@login_required
def index():
    documents = Document.query.order_by(Document.updated_at.desc()).all()
    return render_template('documents/index.html', documents=documents)

@documents_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.can_access('documents'):
        flash('No tienes permisos para crear documentos', 'error')
        return redirect(url_for('documents.index'))

    if request.method == 'POST':
        document = Document(
            title=request.form['title'],
            document_type=request.form['document_type'],
            content=request.form['content'],
            author_id=current_user.id
        )

        db.session.add(document)
        db.session.flush()  # Para obtener el ID del documento

        # Asociar controles SOA seleccionados
        control_ids = request.form.getlist('related_controls')
        if control_ids:
            controls = SOAControl.query.filter(SOAControl.id.in_(control_ids)).all()
            document.related_controls.extend(controls)

        db.session.commit()

        flash('Documento creado correctamente', 'success')
        return redirect(url_for('documents.view', id=document.id))

    # Obtener controles de la versión actual del SOA
    current_version = SOAVersion.get_current_version()
    controls = []
    if current_version:
        controls = SOAControl.query.filter_by(
            soa_version_id=current_version.id
        ).order_by(SOAControl.control_id).all()

    return render_template('documents/create.html', controls=controls)

@documents_bp.route('/<int:id>')
@login_required
def view(id):
    document = Document.query.get_or_404(id)
    return render_template('documents/view.html', document=document)