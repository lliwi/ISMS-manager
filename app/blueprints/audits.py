"""
Blueprint para Gestión de Auditorías
Control 9.2 - Auditoría interna del sistema de gestión de seguridad de la información
"""
from flask import Blueprint, render_template
from flask_login import login_required

audits_bp = Blueprint('audits', __name__)

@audits_bp.route('/')
@login_required
def index():
    """Página de gestión de auditorías - En construcción"""
    return render_template('under_construction.html',
        module_name='Gestión de Auditorías',
        icon='fas fa-clipboard-check',
        description='Sistema integral para planificar, ejecutar y hacer seguimiento de auditorías internas del SGSI conforme a ISO/IEC 27001 y ISO 19011.',
        features=[
            'Planificación de auditorías internas',
            'Programa anual de auditorías',
            'Gestión de auditores calificados',
            'Registro de hallazgos y observaciones',
            'Planes de acción correctiva',
            'Seguimiento de cierre de hallazgos',
            'Informes de auditoría',
            'Evidencias y documentación de auditoría'
        ],
        progress=10
    )

@audits_bp.route('/new')
@login_required
def create():
    """Redirigir a la página principal"""
    return index()

@audits_bp.route('/<int:id>')
@login_required
def view(id):
    """Redirigir a la página principal"""
    return index()
