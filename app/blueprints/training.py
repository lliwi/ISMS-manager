from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import TrainingSession, User, db
from datetime import datetime

training_bp = Blueprint('training', __name__)

@training_bp.route('/')
@login_required
def index():
    sessions = TrainingSession.query.order_by(TrainingSession.date.desc()).all()
    return render_template('training/index.html', sessions=sessions)

@training_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.can_access('training'):
        flash('No tienes permisos para crear sesiones de formación', 'error')
        return redirect(url_for('training.index'))

    if request.method == 'POST':
        session = TrainingSession(
            title=request.form['title'],
            description=request.form['description'],
            training_type=request.form['training_type'],
            duration_hours=float(request.form['duration_hours']),
            date=datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M'),
            trainer_id=current_user.id,
            max_participants=int(request.form['max_participants']) if request.form['max_participants'] else None
        )

        db.session.add(session)
        db.session.commit()

        flash('Sesión de formación creada correctamente', 'success')
        return redirect(url_for('training.view', id=session.id))

    return render_template('training/create.html')

@training_bp.route('/<int:id>')
@login_required
def view(id):
    session = TrainingSession.query.get_or_404(id)
    return render_template('training/view.html', session=session)