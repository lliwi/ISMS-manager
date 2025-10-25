"""
Módulo de Gestión de Riesgos
Sistema de Gestión de Seguridad de la Información (SGSI)

Este módulo implementa la gestión completa de riesgos según ISO 27001:2023
incluyendo apreciación y tratamiento de riesgos.
"""

from flask import Blueprint

# Crear el Blueprint
bp = Blueprint(
    'risks',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/risks'
)

# Importar las rutas después de crear el blueprint para evitar importaciones circulares
from app.risks import routes, models
