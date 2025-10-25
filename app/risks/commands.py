"""
Comandos Flask CLI para el módulo de gestión de riesgos
Permite ejecutar scripts de seed desde la línea de comandos
"""

import click
from flask.cli import with_appcontext


@click.command('seed-risks')
@with_appcontext
def seed_risks_command():
    """
    Carga los catálogos de amenazas y controles para gestión de riesgos.

    Uso:
        flask seed-risks

    O desde Docker:
        docker exec ismsmanager-web-1 flask seed-risks
    """
    from app.risks.seed_all import seed_all_catalogs
    seed_all_catalogs()


@click.command('seed-amenazas')
@with_appcontext
def seed_amenazas_command():
    """
    Carga únicamente el catálogo de amenazas MAGERIT 3.2.

    Uso:
        flask seed-amenazas
    """
    from app.risks.seed_amenazas import seed_amenazas
    seed_amenazas()


@click.command('seed-controles')
@with_appcontext
def seed_controles_command():
    """
    Carga únicamente el catálogo de controles ISO/IEC 27002:2022.

    Uso:
        flask seed-controles
    """
    from app.risks.seed_controles import seed_controles
    seed_controles()


def init_app(app):
    """
    Registra los comandos CLI en la aplicación Flask
    """
    app.cli.add_command(seed_risks_command)
    app.cli.add_command(seed_amenazas_command)
    app.cli.add_command(seed_controles_command)
