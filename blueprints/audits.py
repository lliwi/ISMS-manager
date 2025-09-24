from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Audit, User, db
from datetime import datetime

audits_bp = Blueprint('audits', __name__)

@audits_bp.route('/')
@login_required
def index():
    audits = Audit.query.order_by(Audit.start_date.desc()).all()
    return render_template('audits/index.html', audits=audits)

@audits_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.can_access('audits'):
        flash('No tienes permisos para crear auditorías', 'error')
        return redirect(url_for('audits.index'))

    if request.method == 'POST':
        audit = Audit(
            title=request.form['title'],
            audit_type=request.form['audit_type'],
            scope=request.form['scope'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            lead_auditor_id=current_user.id
        )

        db.session.add(audit)
        db.session.commit()

        flash('Auditoría creada correctamente', 'success')
        return redirect(url_for('audits.view', id=audit.id))

    return render_template('audits/create.html')

@audits_bp.route('/<int:id>')
@login_required
def view(id):
    audit = Audit.query.get_or_404(id)
    return render_template('audits/view.html', audit=audit)