from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import NonConformity, User, db
from datetime import datetime

nonconformities_bp = Blueprint('nonconformities', __name__)

@nonconformities_bp.route('/')
@login_required
def index():
    nonconformities = NonConformity.query.order_by(NonConformity.created_at.desc()).all()
    return render_template('nonconformities/index.html', nonconformities=nonconformities)

@nonconformities_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.can_access('nonconformities'):
        flash('No tienes permisos para crear no conformidades', 'error')
        return redirect(url_for('nonconformities.index'))

    if request.method == 'POST':
        nc = NonConformity(
            title=request.form['title'],
            description=request.form['description'],
            source=request.form['source'],
            severity=request.form['severity'],
            responsible_id=current_user.id
        )

        db.session.add(nc)
        db.session.commit()

        flash('No conformidad creada correctamente', 'success')
        return redirect(url_for('nonconformities.view', id=nc.id))

    return render_template('nonconformities/create.html')

@nonconformities_bp.route('/<int:id>')
@login_required
def view(id):
    nc = NonConformity.query.get_or_404(id)
    return render_template('nonconformities/view.html', nonconformity=nc)