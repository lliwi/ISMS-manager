from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, ISOVersion
from datetime import datetime

auxiliary_bp = Blueprint('auxiliary', __name__)

@auxiliary_bp.route('/iso-versions')
@login_required
def iso_versions():
    """Lista todas las versiones ISO disponibles"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para acceder a esta sección', 'error')
        return redirect(url_for('dashboard.index'))

    versions = ISOVersion.query.order_by(ISOVersion.year.desc()).all()
    return render_template('auxiliary/iso_versions.html', versions=versions)

@auxiliary_bp.route('/iso-versions/new', methods=['GET', 'POST'])
@login_required
def create_iso_version():
    """Crea una nueva versión ISO"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para crear versiones ISO', 'error')
        return redirect(url_for('auxiliary.iso_versions'))

    if request.method == 'POST':
        try:
            version = request.form.get('version')
            year = request.form.get('year')
            title = request.form.get('title')
            description = request.form.get('description')
            number_of_controls = request.form.get('number_of_controls')
            is_active = request.form.get('is_active') == 'on'

            # Validaciones
            if not version or not year or not title:
                flash('Los campos Versión, Año y Título son obligatorios', 'error')
                return render_template('auxiliary/iso_version_form.html', form_data=request.form)

            # Verificar que la versión no exista
            existing_version = ISOVersion.query.filter_by(version=version).first()
            if existing_version:
                flash(f'Ya existe una versión ISO con el código {version}', 'error')
                return render_template('auxiliary/iso_version_form.html', form_data=request.form)

            new_version = ISOVersion(
                version=version,
                year=int(year),
                title=title,
                description=description,
                number_of_controls=int(number_of_controls) if number_of_controls else None,
                is_active=is_active
            )

            db.session.add(new_version)
            db.session.commit()

            flash(f'Versión ISO {version} creada exitosamente', 'success')
            return redirect(url_for('auxiliary.iso_versions'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la versión ISO: {str(e)}', 'error')
            return render_template('auxiliary/iso_version_form.html', form_data=request.form)

    return render_template('auxiliary/iso_version_form.html', form_data=None)

@auxiliary_bp.route('/iso-versions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_iso_version(id):
    """Edita una versión ISO existente"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para editar versiones ISO', 'error')
        return redirect(url_for('auxiliary.iso_versions'))

    version = ISOVersion.query.get_or_404(id)

    if request.method == 'POST':
        try:
            version_code = request.form.get('version')
            year = request.form.get('year')
            title = request.form.get('title')
            description = request.form.get('description')
            number_of_controls = request.form.get('number_of_controls')
            is_active = request.form.get('is_active') == 'on'

            # Validaciones
            if not version_code or not year or not title:
                flash('Los campos Versión, Año y Título son obligatorios', 'error')
                return render_template('auxiliary/iso_version_form.html', version=version, form_data=request.form)

            # Verificar que la versión no exista (excepto la actual)
            existing_version = ISOVersion.query.filter_by(version=version_code).first()
            if existing_version and existing_version.id != id:
                flash(f'Ya existe una versión ISO con el código {version_code}', 'error')
                return render_template('auxiliary/iso_version_form.html', version=version, form_data=request.form)

            version.version = version_code
            version.year = int(year)
            version.title = title
            version.description = description
            version.number_of_controls = int(number_of_controls) if number_of_controls else None
            version.is_active = is_active
            version.updated_at = datetime.utcnow()

            db.session.commit()

            flash(f'Versión ISO {version_code} actualizada exitosamente', 'success')
            return redirect(url_for('auxiliary.iso_versions'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la versión ISO: {str(e)}', 'error')
            return render_template('auxiliary/iso_version_form.html', version=version, form_data=request.form)

    return render_template('auxiliary/iso_version_form.html', version=version, form_data=None)

@auxiliary_bp.route('/iso-versions/<int:id>/delete', methods=['POST'])
@login_required
def delete_iso_version(id):
    """Elimina una versión ISO"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para eliminar versiones ISO', 'error')
        return redirect(url_for('auxiliary.iso_versions'))

    version = ISOVersion.query.get_or_404(id)

    try:
        # TODO: Verificar si la versión está siendo usada en algún SOA
        # Si está en uso, no permitir eliminar

        db.session.delete(version)
        db.session.commit()

        flash(f'Versión ISO {version.version} eliminada exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la versión ISO: {str(e)}', 'error')

    return redirect(url_for('auxiliary.iso_versions'))

@auxiliary_bp.route('/iso-versions/<int:id>/toggle-active', methods=['POST'])
@login_required
def toggle_iso_version_active(id):
    """Activa o desactiva una versión ISO"""
    if not current_user.can_access('soa'):
        flash('No tienes permisos para modificar versiones ISO', 'error')
        return redirect(url_for('auxiliary.iso_versions'))

    version = ISOVersion.query.get_or_404(id)

    try:
        version.is_active = not version.is_active
        version.updated_at = datetime.utcnow()
        db.session.commit()

        status = 'activada' if version.is_active else 'desactivada'
        flash(f'Versión ISO {version.version} {status} exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar el estado de la versión ISO: {str(e)}', 'error')

    return redirect(url_for('auxiliary.iso_versions'))
