from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User, Role, db
from datetime import datetime
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
def index():
    if not current_user.has_role('admin'):
        flash('No tienes permisos de administrador', 'error')
        return redirect(url_for('dashboard.index'))

    users_count = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    return render_template('admin/index.html', users_count=users_count, active_users=active_users)

@admin_bp.route('/users')
@login_required
def users():
    if not current_user.has_role('admin'):
        flash('No tienes permisos de administrador', 'error')
        return redirect(url_for('dashboard.index'))

    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.has_role('admin'):
        flash('No tienes permisos de administrador', 'error')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            department=request.form['department'],
            position=request.form['position'],
            role_id=int(request.form['role_id']),
            password_hash=generate_password_hash(request.form['password'])
        )

        db.session.add(user)
        db.session.commit()

        flash('Usuario creado correctamente', 'success')
        return redirect(url_for('admin.users'))

    roles = Role.query.all()
    return render_template('admin/create_user.html', roles=roles)