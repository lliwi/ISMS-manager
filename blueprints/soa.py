from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import SOAControl, SOAVersion, User, db
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

soa_bp = Blueprint('soa', __name__)

def sort_controls_by_id(controls):
    """Ordena los controles por control_id de forma natural (números primero, luego letras)"""
    def sort_control_id(control):
        control_id = control.control_id
        # Separar por puntos: A.5.1 -> ['A', '5', '1']
        parts = control_id.split('.')

        # Crear una tupla para ordenamiento natural
        sort_key = []
        for part in parts:
            if part.isdigit():
                sort_key.append((0, int(part)))  # (0, número) para que los números vayan primero
            else:
                sort_key.append((1, part))  # (1, letra) para que las letras vayan después

        return sort_key

    return sorted(controls, key=sort_control_id)

@soa_bp.route('/')
@login_required
def index():
    # Obtener la versión actual del SOA o crear una por defecto
    current_version = SOAVersion.get_current_version()
    if not current_version:
        # Crear versión inicial si no existe
        current_version = SOAVersion(
            version_number='1.0',
            title='SOA Inicial - ISO/IEC 27001:2022',
            description='Primera versión del Statement of Applicability',
            iso_version='2022',
            status='active',
            is_current=True,
            created_by_id=current_user.id,
            approval_date=date.today(),
            next_review_date=date.today() + relativedelta(years=1)
        )
        db.session.add(current_version)
        db.session.commit()

    # Obtener controles de la versión actual y ordenarlos
    controls = current_version.controls.all() if current_version else []
    controls = sort_controls_by_id(controls)
    all_versions = SOAVersion.query.order_by(SOAVersion.created_at.desc()).all()

    return render_template('soa/index.html',
                         controls=controls,
                         current_version=current_version,
                         all_versions=all_versions)

@soa_bp.route('/control/<int:id>')
@login_required
def view_control(id):
    control = SOAControl.query.get_or_404(id)
    return render_template('soa/view_control.html', control=control)

@soa_bp.route('/control/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_control(id):
    if not current_user.can_access('soa'):
        flash('No tienes permisos para editar controles SOA', 'error')
        return redirect(url_for('soa.index'))

    control = SOAControl.query.get_or_404(id)

    if request.method == 'POST':
        control.applicability_status = request.form.get('applicability_status', 'aplicable')
        control.justification = request.form['justification']
        control.evidence = request.form['evidence']

        # Actualizar nivel de madurez primero
        control.maturity_level = request.form['maturity_level']

        # Derivar estado de implementación del nivel de madurez y aplicabilidad
        if control.applicability_status == 'transferido':
            control.implementation_status = 'implemented'  # Los transferidos se consideran implementados
            control.transfer_details = request.form.get('transfer_details', '')
        elif control.applicability_status == 'no_aplicable':
            control.implementation_status = 'not_implemented'
            control.transfer_details = None
        else:  # aplicable
            # Para controles aplicables, derivar del nivel de madurez
            if control.maturity_level == 'no_implementado':
                control.implementation_status = 'not_implemented'
            else:
                control.implementation_status = 'implemented'
            control.transfer_details = None
        control.responsible_user_id = int(request.form['responsible_user_id']) if request.form['responsible_user_id'] else None

        # Fecha objetivo
        if request.form.get('target_date'):
            control.target_date = datetime.strptime(request.form['target_date'], '%Y-%m-%d').date()
        else:
            control.target_date = None

        db.session.commit()
        flash('Control actualizado correctamente', 'success')
        return redirect(url_for('soa.view_control', id=control.id))

    users = User.query.filter_by(is_active=True).all()
    return render_template('soa/edit_control.html', control=control, users=users)

# === GESTIÓN DE VERSIONES SOA ===

@soa_bp.route('/versions')
@login_required
def versions():
    if not current_user.can_access('soa'):
        flash('No tienes permisos para gestionar versiones SOA', 'error')
        return redirect(url_for('soa.index'))

    versions = SOAVersion.query.order_by(SOAVersion.created_at.desc()).all()
    return render_template('soa/versions.html', versions=versions)

@soa_bp.route('/versions/new', methods=['GET', 'POST'])
@login_required
def create_version():
    if not current_user.can_access('soa'):
        flash('No tienes permisos para crear versiones SOA', 'error')
        return redirect(url_for('soa.index'))

    if request.method == 'POST':
        # Crear nueva versión
        new_version = SOAVersion(
            version_number=request.form['version_number'],
            title=request.form['title'],
            description=request.form['description'],
            iso_version=request.form['iso_version'],
            status='draft',
            created_by_id=current_user.id
        )

        # Establecer fechas
        if request.form['approval_date']:
            new_version.approval_date = datetime.strptime(request.form['approval_date'], '%Y-%m-%d').date()

        if request.form['next_review_date']:
            new_version.next_review_date = datetime.strptime(request.form['next_review_date'], '%Y-%m-%d').date()

        db.session.add(new_version)
        db.session.flush()  # Para obtener el ID

        # Copiar controles de la versión base si se especifica
        base_version_id = request.form.get('base_version_id')
        if base_version_id:
            base_version = SOAVersion.query.get(base_version_id)
            if base_version:
                for base_control in base_version.controls:
                    new_control = SOAControl(
                        control_id=base_control.control_id,
                        title=base_control.title,
                        description=base_control.description,
                        category=base_control.category,
                        applicability_status=base_control.applicability_status or ('aplicable' if base_control.is_applicable else 'no_aplicable'),
                        justification=base_control.justification,
                        transfer_details=base_control.transfer_details,
                        implementation_status=base_control.implementation_status,
                        maturity_level=base_control.maturity_level,
                        responsible_user_id=base_control.responsible_user_id,
                        target_date=base_control.target_date,
                        soa_version_id=new_version.id
                    )
                    db.session.add(new_control)

        db.session.commit()
        flash('Nueva versión SOA creada correctamente', 'success')
        return redirect(url_for('soa.view_version', id=new_version.id))

    # Para GET: obtener versiones existentes para usar como base
    existing_versions = SOAVersion.query.order_by(SOAVersion.created_at.desc()).all()
    return render_template('soa/create_version.html', existing_versions=existing_versions)

@soa_bp.route('/versions/<int:id>')
@login_required
def view_version(id):
    version = SOAVersion.query.get_or_404(id)
    controls = sort_controls_by_id(version.controls.all())

    # Estadísticas de la versión
    stats = {
        'total_controls': len(controls),
        'aplicable': len([c for c in controls if (c.applicability_status or ('aplicable' if c.is_applicable else 'no_aplicable')) == 'aplicable']),
        'transferido': len([c for c in controls if (c.applicability_status or ('aplicable' if c.is_applicable else 'no_aplicable')) == 'transferido']),
        'no_aplicable': len([c for c in controls if (c.applicability_status or ('aplicable' if c.is_applicable else 'no_aplicable')) == 'no_aplicable']),
        'implemented': len([c for c in controls if c.implementation_status == 'implemented']),
        'not_implemented': len([c for c in controls if c.implementation_status == 'not_implemented' or c.implementation_status == 'pending'])
    }

    return render_template('soa/view_version.html', version=version, controls=controls, stats=stats)

@soa_bp.route('/versions/<int:id>/activate', methods=['POST'])
@login_required
def activate_version(id):
    if not current_user.can_access('soa'):
        flash('No tienes permisos para activar versiones SOA', 'error')
        return redirect(url_for('soa.versions'))

    version = SOAVersion.query.get_or_404(id)
    version.set_as_current()

    flash(f'Versión {version.version_number} activada como versión actual', 'success')
    return redirect(url_for('soa.view_version', id=version.id))

@soa_bp.route('/versions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_version(id):
    if not current_user.can_access('soa'):
        flash('No tienes permisos para editar versiones SOA', 'error')
        return redirect(url_for('soa.versions'))

    version = SOAVersion.query.get_or_404(id)

    if request.method == 'POST':
        version.version_number = request.form['version_number']
        version.title = request.form['title']
        version.description = request.form['description']
        version.iso_version = request.form['iso_version']

        # Establecer fechas
        if request.form['approval_date']:
            version.approval_date = datetime.strptime(request.form['approval_date'], '%Y-%m-%d').date()
        else:
            version.approval_date = None

        if request.form['next_review_date']:
            version.next_review_date = datetime.strptime(request.form['next_review_date'], '%Y-%m-%d').date()
        else:
            version.next_review_date = None

        db.session.commit()
        flash('Versión SOA actualizada correctamente', 'success')
        return redirect(url_for('soa.view_version', id=version.id))

    return render_template('soa/edit_version.html', version=version)

@soa_bp.route('/versions/<int:id>/delete', methods=['POST'])
@login_required
def delete_version(id):
    if not current_user.can_access('soa'):
        flash('No tienes permisos para eliminar versiones SOA', 'error')
        return redirect(url_for('soa.versions'))

    version = SOAVersion.query.get_or_404(id)

    # No permitir eliminar la versión actual
    if version.is_current:
        flash('No se puede eliminar la versión actual del SOA', 'error')
        return redirect(url_for('soa.versions'))

    # Verificar si hay al menos otra versión
    total_versions = SOAVersion.query.count()
    if total_versions <= 1:
        flash('No se puede eliminar la única versión del SOA', 'error')
        return redirect(url_for('soa.versions'))

    try:
        # Eliminar todos los controles asociados primero
        for control in version.controls:
            db.session.delete(control)

        # Eliminar la versión
        db.session.delete(version)
        db.session.commit()
        flash(f'Versión {version.version_number} eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar la versión. Inténtelo de nuevo.', 'error')

    return redirect(url_for('soa.versions'))

@soa_bp.route('/versions/<int:id1>/compare/<int:id2>')
@login_required
def compare_versions(id1, id2):
    version1 = SOAVersion.query.get_or_404(id1)
    version2 = SOAVersion.query.get_or_404(id2)

    controls1 = {c.control_id: c for c in version1.controls}
    controls2 = {c.control_id: c for c in version2.controls}

    # Analizar diferencias
    all_control_ids = set(controls1.keys()) | set(controls2.keys())
    comparison = []

    for control_id in sorted(all_control_ids):
        c1 = controls1.get(control_id)
        c2 = controls2.get(control_id)

        if c1 and c2:
            # Control existe en ambas versiones
            changes = {}
            status1 = c1.applicability_status or ('aplicable' if c1.is_applicable else 'no_aplicable')
            status2 = c2.applicability_status or ('aplicable' if c2.is_applicable else 'no_aplicable')
            if status1 != status2:
                changes['applicability'] = {'old': status1, 'new': status2}
            if c1.implementation_status != c2.implementation_status:
                changes['status'] = {'old': c1.implementation_status, 'new': c2.implementation_status}
            if c1.maturity_level != c2.maturity_level:
                changes['maturity'] = {'old': c1.maturity_level, 'new': c2.maturity_level}
            if c1.responsible_user_id != c2.responsible_user_id:
                changes['responsible'] = {
                    'old': c1.responsible.full_name if c1.responsible else None,
                    'new': c2.responsible.full_name if c2.responsible else None
                }

            comparison.append({
                'control_id': control_id,
                'title': c1.title or c2.title,
                'status': 'modified' if changes else 'unchanged',
                'changes': changes,
                'control1': c1,
                'control2': c2
            })
        elif c1:
            # Control solo en versión 1
            comparison.append({
                'control_id': control_id,
                'title': c1.title,
                'status': 'removed',
                'control1': c1,
                'control2': None
            })
        else:
            # Control solo en versión 2
            comparison.append({
                'control_id': control_id,
                'title': c2.title,
                'status': 'added',
                'control1': None,
                'control2': c2
            })

    return render_template('soa/compare_versions.html',
                         version1=version1,
                         version2=version2,
                         comparison=comparison)

@soa_bp.route('/versions/<int:id>/clone', methods=['GET', 'POST'])
@login_required
def clone_version(id):
    if not current_user.can_access('soa'):
        flash('No tienes permisos para clonar versiones SOA', 'error')
        return redirect(url_for('soa.versions'))

    source_version = SOAVersion.query.get_or_404(id)

    if request.method == 'POST':
        # Crear nueva versión basada en la fuente
        new_version = SOAVersion(
            version_number=request.form['version_number'],
            title=request.form['title'],
            description=request.form['description'],
            iso_version=source_version.iso_version,  # Mantener la misma versión ISO
            status='draft',  # Siempre crear como borrador
            created_by_id=current_user.id
        )

        # Establecer fechas si se proporcionan
        if request.form.get('approval_date'):
            new_version.approval_date = datetime.strptime(request.form['approval_date'], '%Y-%m-%d').date()

        if request.form.get('next_review_date'):
            new_version.next_review_date = datetime.strptime(request.form['next_review_date'], '%Y-%m-%d').date()

        db.session.add(new_version)
        db.session.flush()  # Para obtener el ID

        # Clonar todos los controles de la versión fuente
        for source_control in source_version.controls:
            new_control = SOAControl(
                control_id=source_control.control_id,
                title=source_control.title,
                description=source_control.description,
                category=source_control.category,
                applicability_status=source_control.applicability_status or ('aplicable' if source_control.is_applicable else 'no_aplicable'),
                justification=source_control.justification,
                transfer_details=source_control.transfer_details,
                implementation_status=source_control.implementation_status,
                maturity_level=source_control.maturity_level,
                responsible_user_id=source_control.responsible_user_id,
                target_date=source_control.target_date,
                evidence=source_control.evidence,
                soa_version_id=new_version.id
            )
            db.session.add(new_control)

        db.session.commit()
        flash(f'Versión SOA {new_version.version_number} clonada correctamente desde v{source_version.version_number}', 'success')
        return redirect(url_for('soa.view_version', id=new_version.id))

    # Para GET: mostrar formulario de clonación
    # Generar sugerencia de número de versión
    latest_version = SOAVersion.query.order_by(SOAVersion.created_at.desc()).first()
    if latest_version:
        try:
            # Intentar incrementar el número de versión
            parts = latest_version.version_number.split('.')
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            suggested_version = f"{major}.{minor + 1}"
        except (ValueError, IndexError):
            suggested_version = "1.1"
    else:
        suggested_version = "1.0"

    return render_template('soa/clone_version.html',
                         source_version=source_version,
                         suggested_version=suggested_version)