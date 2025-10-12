"""
Blueprint para Gestión de Tareas Periódicas
Control 5.37 - Procedimientos operativos documentados
"""
from flask import Blueprint, render_template
from flask_login import login_required

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/')
@login_required
def index():
    """Página de gestión de tareas - En construcción"""
    return render_template('under_construction.html',
        module_name='Gestión de Tareas',
        icon='fas fa-tasks',
        description='Sistema de gestión de tareas periódicas y actividades operativas del SGSI con seguimiento y recordatorios automáticos.',
        features=[
            'Creación de tareas periódicas',
            'Calendario de tareas',
            'Asignación y delegación',
            'Recordatorios automáticos',
            'Tareas recurrentes (diarias, semanales, mensuales, anuales)',
            'Estado de cumplimiento',
            'Historial de ejecución',
            'Notificaciones por email',
            'Dashboard de tareas pendientes',
            'Reportes de cumplimiento'
        ],
        progress=10
    )

@tasks_bp.route('/new')
@login_required
def create():
    """Redirigir a la página principal"""
    return index()

@tasks_bp.route('/<int:id>')
@login_required
def view(id):
    """Redirigir a la página principal"""
    return index()
