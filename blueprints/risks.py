"""
Blueprint para Gestión de Riesgos
Control 6.1.2 - Evaluación de riesgos de seguridad de la información
"""
from flask import Blueprint, render_template
from flask_login import login_required

risks_bp = Blueprint('risks', __name__)

@risks_bp.route('/')
@login_required
def index():
    """Página de gestión de riesgos - En construcción"""
    return render_template('under_construction.html',
        module_name='Gestión de Riesgos',
        icon='fas fa-exclamation-triangle',
        description='Sistema completo para la identificación, evaluación, tratamiento y monitoreo de riesgos de seguridad de la información según ISO/IEC 27001.',
        features=[
            'Identificación y registro de riesgos',
            'Evaluación de probabilidad e impacto',
            'Matriz de riesgos visual',
            'Planes de tratamiento de riesgos',
            'Análisis de activos y amenazas',
            'Seguimiento de controles mitigadores',
            'Reportes y dashboards de riesgos',
            'Revisión periódica de riesgos'
        ],
        progress=15
    )

@risks_bp.route('/new')
@login_required
def create():
    """Redirigir a la página principal"""
    return index()

@risks_bp.route('/<int:id>')
@login_required
def view(id):
    """Redirigir a la página principal"""
    return index()
