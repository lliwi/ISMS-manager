from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Task, User, db
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
@login_required
def index():
    tasks = Task.query.filter_by(assignee_id=current_user.id).order_by(Task.due_date).all()
    return render_template('tasks/index.html', tasks=tasks)

@tasks_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.can_access('tasks'):
        flash('No tienes permisos para crear tareas', 'error')
        return redirect(url_for('tasks.index'))

    if request.method == 'POST':
        task = Task(
            title=request.form['title'],
            description=request.form['description'],
            task_type=request.form['task_type'],
            frequency=request.form['frequency'],
            due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%dT%H:%M'),
            assignee_id=int(request.form['assignee_id'])
        )

        db.session.add(task)
        db.session.commit()

        flash('Tarea creada correctamente', 'success')
        return redirect(url_for('tasks.view', id=task.id))

    users = User.query.filter_by(is_active=True).all()
    return render_template('tasks/create.html', users=users)

@tasks_bp.route('/<int:id>')
@login_required
def view(id):
    task = Task.query.get_or_404(id)
    return render_template('tasks/view.html', task=task)