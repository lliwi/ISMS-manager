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


@click.command('seed-control-amenaza')
@with_appcontext
def seed_control_amenaza_command():
    """
    Carga las relaciones control-amenaza según mejores prácticas.

    Mapea controles ISO 27002:2022 con amenazas MAGERIT 3.2.
    Necesario para que el cálculo de riesgos funcione.

    Uso:
        flask seed-control-amenaza

    O desde Docker:
        docker exec ismsmanager-web-1 flask seed-control-amenaza
    """
    from app.risks.seed_control_amenaza import seed_control_amenaza
    seed_control_amenaza()


@click.command('seed-amenaza-recurso')
@with_appcontext
def seed_amenaza_recurso_command():
    """
    Carga las relaciones amenaza-recurso-tipo según MAGERIT 3.2.

    Define qué amenazas aplican a qué tipos de recursos y con qué frecuencia.
    CRÍTICO para que el cálculo de riesgos funcione.

    Uso:
        flask seed-amenaza-recurso

    O desde Docker:
        docker exec ismsmanager-web-1 flask seed-amenaza-recurso
    """
    from app.risks.seed_amenaza_recurso import seed_amenaza_recurso
    seed_amenaza_recurso()


def init_app(app):
    """
    Registra los comandos CLI en la aplicación Flask
    """
    app.cli.add_command(seed_risks_command)
    app.cli.add_command(seed_amenazas_command)
    app.cli.add_command(seed_controles_command)
    app.cli.add_command(seed_control_amenaza_command)
    app.cli.add_command(seed_amenaza_recurso_command)
