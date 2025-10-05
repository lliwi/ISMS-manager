"""
Blueprint para Gestión de No Conformidades
Control 10.1 - No conformidad y acción correctiva
"""
from flask import Blueprint, render_template
from flask_login import login_required

nonconformities_bp = Blueprint('nonconformities', __name__)

@nonconformities_bp.route('/')
@login_required
def index():
    """Página de gestión de no conformidades - En construcción"""
    return render_template('under_construction.html',
        module_name='Gestión de No Conformidades',
        icon='fas fa-exclamation-circle',
        description='Sistema para detectar, registrar y gestionar no conformidades con acciones correctivas y preventivas según ISO/IEC 27001.',
        features=[
            'Registro de no conformidades',
            'Clasificación por severidad y origen',
            'Análisis de causa raíz (RCA)',
            'Definición de acciones correctivas',
            'Acciones preventivas',
            'Seguimiento de implementación',
            'Verificación de eficacia',
            'Indicadores de no conformidades',
            'Lecciones aprendidas'
        ],
        progress=10
    )

@nonconformities_bp.route('/new')
@login_required
def create():
    """Redirigir a la página principal"""
    return index()

@nonconformities_bp.route('/<int:id>')
@login_required
def view(id):
    """Redirigir a la página principal"""
    return index()
