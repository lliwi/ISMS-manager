from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Risk, User, db
from datetime import datetime

risks_bp = Blueprint('risks', __name__)

@risks_bp.route('/')
@login_required
def index():
    risks = Risk.query.order_by(Risk.created_at.desc()).all()
    return render_template('risks/index.html', risks=risks)

@risks_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.can_access('risks'):
        flash('No tienes permisos para crear riesgos', 'error')
        return redirect(url_for('risks.index'))

    if request.method == 'POST':
        risk = Risk(
            title=request.form['title'],
            description=request.form['description'],
            category=request.form['category'],
            probability=int(request.form['probability']),
            impact=int(request.form['impact']),
            treatment=request.form['treatment'],
            treatment_description=request.form['treatment_description'],
            owner_id=current_user.id
        )
        risk.risk_level = risk.calculate_risk_level()

        db.session.add(risk)
        db.session.commit()

        flash('Riesgo creado correctamente', 'success')
        return redirect(url_for('risks.view', id=risk.id))

    return render_template('risks/create.html')

@risks_bp.route('/<int:id>')
@login_required
def view(id):
    risk = Risk.query.get_or_404(id)
    return render_template('risks/view.html', risk=risk)