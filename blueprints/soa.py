from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import SOAControl, SOAVersion, User, db
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

soa_bp = Blueprint('soa', __name__)

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

    # Obtener controles de la versión actual
    controls = current_version.controls.all() if current_version else []
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
        control.is_applicable = request.form.get('is_applicable') == 'on'
        control.justification = request.form['justification']
        control.evidence = request.form['evidence']
        control.implementation_status = request.form['implementation_status']
        control.maturity_level = request.form['maturity_level']
        control.responsible_user_id = int(request.form['responsible_user_id']) if request.form['responsible_user_id'] else None

        # Fecha objetivo
        if request.form['target_date']:
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
                        is_applicable=base_control.is_applicable,
                        justification=base_control.justification,
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
    controls = version.controls.all()

    # Estadísticas de la versión
    stats = {
        'total_controls': len(controls),
        'applicable': len([c for c in controls if c.is_applicable]),
        'implemented': len([c for c in controls if c.implementation_status == 'implemented']),
        'pending': len([c for c in controls if c.implementation_status == 'pending']),
        'not_applicable': len([c for c in controls if c.implementation_status == 'not_applicable'])
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
            if c1.is_applicable != c2.is_applicable:
                changes['applicability'] = {'old': c1.is_applicable, 'new': c2.is_applicable}
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