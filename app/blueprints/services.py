"""
Blueprint para Gestión de Servicios - ISO 27001:2023
Control 5.9 - Inventario de activos
Control 8.1 - Responsabilidad sobre los activos

Este módulo permite gestionar servicios de TI y negocio, sus dependencias
y la asociación con activos del inventario.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from datetime import datetime
from models import db, Service, ServiceType, ServiceStatus, Asset, User, ServiceDependency
from utils.decorators import role_required
from app.risks.models import Riesgo, ActivoInformacion

services_bp = Blueprint('services', __name__, url_prefix='/servicios')


def generate_service_code(service_type):
    """
    Genera un código único para el servicio basándose en el tipo
    Formato: TIPO-NNNNN
    Ejemplos: IT-00001, BUS-00001, SUPP-00001
    """
    # Prefijos según el tipo de servicio
    type_prefixes = {
        'IT': 'IT',           # Servicios de TI
        'BUSINESS': 'BUS',    # Servicios de negocio
        'SUPPORT': 'SUPP',    # Servicios de soporte
        'CLOUD': 'CLD',       # Servicios en la nube
        'EXTERNAL': 'EXT'     # Servicios externos
    }

    prefix = type_prefixes.get(service_type, 'SRV')

    # Obtener el último número para este tipo
    last_service = Service.query.filter(
        Service.service_code.like(f'{prefix}-%')
    ).order_by(Service.service_code.desc()).first()

    if last_service:
        try:
            # Extraer el número del código (formato: PREFIX-NNNNN)
            last_num = int(last_service.service_code.split('-')[1])
            new_num = last_num + 1
        except (IndexError, ValueError):
            new_num = 1
    else:
        new_num = 1

    # Generar código con formato PREFIX-NNNNN (5 dígitos con ceros a la izquierda)
    return f"{prefix}-{new_num:05d}"


def check_circular_dependency(service_id, depends_on_id, visited=None):
    """
    Verifica si agregar una dependencia crearía un ciclo
    Retorna True si se detecta un ciclo, False si es seguro
    """
    if visited is None:
        visited = set()

    # Si volvemos al servicio original, hay un ciclo
    if depends_on_id == service_id:
        return True

    # Si ya visitamos este nodo, no hay ciclo en esta rama
    if depends_on_id in visited:
        return False

    visited.add(depends_on_id)

    # Verificar las dependencias del servicio del que dependemos
    dependencies = ServiceDependency.query.filter_by(service_id=depends_on_id).all()
    for dep in dependencies:
        if check_circular_dependency(service_id, dep.depends_on_service_id, visited.copy()):
            return True

    return False


@services_bp.route('/')
@login_required
def index():
    """Lista todos los servicios con filtros opcionales"""
    # Obtener parámetros de filtro
    service_type = request.args.get('type', '')
    status = request.args.get('status', '')
    department = request.args.get('department', '')
    search = request.args.get('search', '')
    criticality_min = request.args.get('criticality_min', type=int)

    # Construir query base
    query = Service.query

    # Aplicar filtros
    if service_type:
        query = query.filter(Service.service_type == ServiceType[service_type])

    if status:
        query = query.filter(Service.status == ServiceStatus[status])

    if department:
        query = query.filter(Service.department == department)

    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(
            Service.name.ilike(search_term),
            Service.service_code.ilike(search_term),
            Service.description.ilike(search_term)
        ))

    if criticality_min:
        query = query.filter(Service.criticality >= criticality_min)

    # Ordenar por código de servicio
    services = query.order_by(Service.service_code).all()

    # Calcular estadísticas
    total_services = Service.query.count()
    active_services = Service.query.filter(Service.status == ServiceStatus.ACTIVE).count()
    critical_services = Service.query.filter(Service.criticality >= 8).count()

    # Obtener departamentos únicos para filtro
    departments = db.session.query(Service.department).distinct().filter(
        Service.department.isnot(None)
    ).all()
    departments = [d[0] for d in departments]

    return render_template('services/index.html',
                         services=services,
                         service_types=ServiceType,
                         service_statuses=ServiceStatus,
                         departments=departments,
                         total_services=total_services,
                         active_services=active_services,
                         critical_services=critical_services,
                         filters={
                             'type': service_type,
                             'status': status,
                             'department': department,
                             'search': search,
                             'criticality_min': criticality_min
                         })


@services_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def create():
    """Crear nuevo servicio"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            service_code = request.form.get('service_code', '').strip()
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            service_type = request.form.get('service_type')
            status = request.form.get('status', 'ACTIVE')
            service_owner_id = request.form.get('service_owner_id', type=int)
            technical_manager_id = request.form.get('technical_manager_id', type=int)
            criticality = request.form.get('criticality', type=int)
            required_availability = request.form.get('required_availability', type=float)
            rto = request.form.get('rto', type=int)
            rpo = request.form.get('rpo', type=int)
            operating_hours = request.form.get('operating_hours', '').strip()
            department = request.form.get('department', '').strip()
            annual_cost = request.form.get('annual_cost', type=float)

            # Validaciones
            if not name or not service_type or not service_owner_id:
                flash('Nombre, tipo y propietario son obligatorios', 'error')
                return redirect(url_for('services.create'))

            # Generar código automáticamente si no se proporciona
            if not service_code:
                service_code = generate_service_code(service_type)

            # Verificar si el código ya existe
            existing = Service.query.filter_by(service_code=service_code).first()
            if existing:
                flash(f'Ya existe un servicio con el código {service_code}', 'error')
                return redirect(url_for('services.create'))

            # Crear nuevo servicio
            service = Service(
                service_code=service_code,
                name=name,
                description=description if description else None,
                service_type=ServiceType[service_type],
                status=ServiceStatus[status],
                service_owner_id=service_owner_id,
                technical_manager_id=technical_manager_id if technical_manager_id else None,
                criticality=criticality if criticality else 5,
                required_availability=required_availability,
                rto=rto,
                rpo=rpo,
                operating_hours=operating_hours if operating_hours else None,
                department=department if department else None,
                annual_cost=annual_cost,
                created_by_id=current_user.id,
                created_at=datetime.utcnow()
            )

            db.session.add(service)
            db.session.flush()  # Para obtener el ID del servicio

            # Manejar activos asociados
            asset_ids = request.form.getlist('asset_ids')
            if asset_ids:
                assets = Asset.query.filter(Asset.id.in_(asset_ids)).all()
                service.assets = assets

            # Manejar dependencias de servicios
            dependency_service_ids = request.form.getlist('dependency_service_ids')
            if dependency_service_ids:
                for dep_service_id in dependency_service_ids:
                    dep_service_id_int = int(dep_service_id)

                    # Validar que no sea el mismo servicio
                    if dep_service_id_int == service.id:
                        flash('Un servicio no puede depender de sí mismo', 'warning')
                        continue

                    # Verificar dependencias circulares
                    if check_circular_dependency(service.id, dep_service_id_int):
                        dep_service = Service.query.get(dep_service_id_int)
                        flash(f'No se puede agregar dependencia con {dep_service.service_code}: crearía un ciclo de dependencias', 'warning')
                        continue

                    # Obtener el tipo de dependencia
                    dep_type_key = f'dependency_types_{dep_service_id}'
                    dep_type = request.form.get(dep_type_key, 'required')

                    # Crear la dependencia
                    dependency = ServiceDependency(
                        service_id=service.id,
                        depends_on_service_id=dep_service_id_int,
                        dependency_type=dep_type,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(dependency)

            db.session.commit()

            flash(f'Servicio {service_code} creado exitosamente', 'success')
            return redirect(url_for('services.detail', service_id=service.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear servicio: {str(e)}', 'error')
            return redirect(url_for('services.create'))

    # GET: Mostrar formulario
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    # Obtener todos los activos (el template maneja los que no tienen tipo)
    assets = Asset.query.order_by(Asset.asset_code).all()
    # Obtener todos los servicios para dependencias
    all_services = Service.query.order_by(Service.service_code).all()

    return render_template('services/form.html',
                         service=None,
                         service_types=ServiceType,
                         service_statuses=ServiceStatus,
                         users=users,
                         assets=assets,
                         services=all_services,
                         action='create')


@services_bp.route('/<int:service_id>')
@login_required
def detail(service_id):
    """Ver detalles de un servicio"""
    service = Service.query.get_or_404(service_id)

    # Obtener dependencias (servicios de los que depende este)
    dependencies = ServiceDependency.query.filter_by(
        service_id=service_id
    ).all()

    # Obtener dependientes (servicios que dependen de este)
    dependents = ServiceDependency.query.filter_by(
        depends_on_service_id=service_id
    ).all()

    # Obtener activos asociados
    assets = list(service.assets)

    return render_template('services/detail.html',
                         service=service,
                         dependencies=dependencies,
                         dependents=dependents,
                         assets=assets)


@services_bp.route('/<int:service_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'ciso')
def edit(service_id):
    """Editar un servicio existente"""
    service = Service.query.get_or_404(service_id)

    if request.method == 'POST':
        try:
            # Actualizar datos del formulario
            service.service_code = request.form.get('service_code', '').strip()
            service.name = request.form.get('name', '').strip()
            service.description = request.form.get('description', '').strip()
            service.service_type = ServiceType[request.form.get('service_type')]
            service.status = ServiceStatus[request.form.get('status', 'ACTIVE')]
            service.service_owner_id = request.form.get('service_owner_id', type=int)
            service.technical_manager_id = request.form.get('technical_manager_id', type=int)
            service.criticality = request.form.get('criticality', type=int) or 5
            service.required_availability = request.form.get('required_availability', type=float)
            service.rto = request.form.get('rto', type=int)
            service.rpo = request.form.get('rpo', type=int)
            service.operating_hours = request.form.get('operating_hours', '').strip() or None
            service.department = request.form.get('department', '').strip() or None
            service.annual_cost = request.form.get('annual_cost', type=float)
            service.updated_at = datetime.utcnow()
            service.updated_by_id = current_user.id

            # Validaciones
            if not service.service_code or not service.name or not service.service_owner_id:
                flash('Código, nombre y propietario son obligatorios', 'error')
                return redirect(url_for('services.edit', service_id=service_id))

            # Verificar código duplicado (excepto el actual)
            existing = Service.query.filter(
                Service.service_code == service.service_code,
                Service.id != service_id
            ).first()
            if existing:
                flash(f'Ya existe otro servicio con el código {service.service_code}', 'error')
                return redirect(url_for('services.edit', service_id=service_id))

            # Manejar activos asociados
            asset_ids = request.form.getlist('asset_ids')
            if asset_ids:
                assets = Asset.query.filter(Asset.id.in_(asset_ids)).all()
                service.assets = assets
            else:
                service.assets = []

            # Manejar dependencias de servicios
            # Primero eliminar las dependencias existentes
            ServiceDependency.query.filter_by(service_id=service_id).delete()

            # Crear las nuevas dependencias
            dependency_service_ids = request.form.getlist('dependency_service_ids')
            if dependency_service_ids:
                for dep_service_id in dependency_service_ids:
                    dep_service_id_int = int(dep_service_id)

                    # Validar que no sea el mismo servicio
                    if dep_service_id_int == service_id:
                        flash('Un servicio no puede depender de sí mismo', 'warning')
                        continue

                    # Verificar dependencias circulares
                    if check_circular_dependency(service_id, dep_service_id_int):
                        dep_service = Service.query.get(dep_service_id_int)
                        flash(f'No se puede agregar dependencia con {dep_service.service_code}: crearía un ciclo de dependencias', 'warning')
                        continue

                    # Obtener el tipo de dependencia
                    dep_type_key = f'dependency_types_{dep_service_id}'
                    dep_type = request.form.get(dep_type_key, 'required')

                    # Crear la dependencia
                    dependency = ServiceDependency(
                        service_id=service_id,
                        depends_on_service_id=dep_service_id_int,
                        dependency_type=dep_type,
                        created_at=datetime.utcnow()
                    )
                    db.session.add(dependency)

            db.session.commit()

            flash(f'Servicio {service.service_code} actualizado exitosamente', 'success')
            return redirect(url_for('services.detail', service_id=service.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar servicio: {str(e)}', 'error')
            return redirect(url_for('services.edit', service_id=service_id))

    # GET: Mostrar formulario con datos actuales
    users = User.query.filter_by(is_active=True).order_by(User.username).all()
    # Obtener todos los activos (el template maneja los que no tienen tipo)
    assets = Asset.query.order_by(Asset.asset_code).all()
    # Obtener todos los servicios para dependencias (excluyendo el actual)
    all_services = Service.query.order_by(Service.service_code).all()

    return render_template('services/form.html',
                         service=service,
                         service_types=ServiceType,
                         service_statuses=ServiceStatus,
                         users=users,
                         assets=assets,
                         services=all_services,
                         action='edit')


@services_bp.route('/<int:service_id>/eliminar', methods=['POST'])
@login_required
@role_required('admin', 'ciso')
def delete(service_id):
    """Eliminar un servicio (soft delete cambiando status a DEPRECATED)"""
    try:
        service = Service.query.get_or_404(service_id)

        # Verificar si hay servicios que dependen de este
        dependents = ServiceDependency.query.filter_by(
            depends_on_service_id=service_id
        ).count()

        if dependents > 0:
            flash(f'No se puede eliminar {service.service_code} porque otros servicios dependen de él', 'error')
            return redirect(url_for('services.detail', service_id=service_id))

        # Soft delete: cambiar estado a DEPRECATED
        service.status = ServiceStatus.DEPRECATED
        service.updated_at = datetime.utcnow()
        service.updated_by_id = current_user.id

        db.session.commit()

        flash(f'Servicio {service.service_code} marcado como obsoleto', 'success')
        return redirect(url_for('services.index'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar servicio: {str(e)}', 'error')
        return redirect(url_for('services.detail', service_id=service_id))


@services_bp.route('/<int:service_id>/activos')
@login_required
def service_assets(service_id):
    """Ver activos asociados a un servicio"""
    service = Service.query.get_or_404(service_id)
    assets = list(service.assets)

    return render_template('services/assets.html',
                         service=service,
                         assets=assets)


@services_bp.route('/<int:service_id>/dependencias')
@login_required
def service_dependencies(service_id):
    """Ver dependencias de un servicio"""
    service = Service.query.get_or_404(service_id)

    # Obtener dependencias (servicios de los que depende este)
    dependencies = ServiceDependency.query.filter_by(
        service_id=service_id
    ).all()

    # Obtener dependientes (servicios que dependen de este)
    dependents = ServiceDependency.query.filter_by(
        depends_on_service_id=service_id
    ).all()

    return render_template('services/dependencies.html',
                         service=service,
                         dependencies=dependencies,
                         dependents=dependents)


@services_bp.route('/api/search')
@login_required
def api_search():
    """API para búsqueda de servicios (para autocompletar)"""
    query = request.args.get('q', '').strip()

    if not query or len(query) < 2:
        return jsonify([])

    search_term = f"%{query}%"
    services = Service.query.filter(
        or_(
            Service.name.ilike(search_term),
            Service.service_code.ilike(search_term)
        ),
        Service.status == ServiceStatus.ACTIVE
    ).limit(10).all()

    results = [{
        'id': s.id,
        'service_code': s.service_code,
        'name': s.name,
        'type': s.service_type.name,
        'criticality': s.criticality
    } for s in services]

    return jsonify(results)


@services_bp.route('/api/generate-code')
@login_required
def api_generate_code():
    """API para generar código de servicio automáticamente"""
    service_type = request.args.get('type', '').strip()

    if not service_type:
        return jsonify({'error': 'Tipo de servicio requerido'}), 400

    try:
        # Validar que el tipo de servicio existe
        if service_type not in [t.name for t in ServiceType]:
            return jsonify({'error': 'Tipo de servicio inválido'}), 400

        # Generar código
        service_code = generate_service_code(service_type)

        return jsonify({
            'service_code': service_code,
            'type': service_type
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== HELPER FUNCTIONS ====================

def get_risks_for_service(service):
    """
    Obtiene todos los riesgos asociados a un servicio a través de sus activos.
    Vincula Asset (código) con ActivoInformacion (código) y luego con Riesgo.

    Args:
        service: Instancia de Service

    Returns:
        list: Lista de objetos Riesgo asociados al servicio
    """
    # Obtener códigos de los activos del servicio
    asset_codes = [asset.asset_code for asset in service.assets if asset.asset_code]

    if not asset_codes:
        return []

    # Buscar ActivoInformacion por código
    activos_info = ActivoInformacion.query.filter(
        ActivoInformacion.codigo.in_(asset_codes)
    ).all()

    activos_ids = [activo.id for activo in activos_info]

    if not activos_ids:
        return []

    # Obtener riesgos asociados a esos activos
    riesgos = Riesgo.query.filter(
        Riesgo.activo_id.in_(activos_ids)
    ).order_by(Riesgo.nivel_riesgo_efectivo.desc()).all()

    return riesgos


def calculate_service_risk_stats(service):
    """
    Calcula estadísticas de riesgos para un servicio.

    Args:
        service: Instancia de Service

    Returns:
        dict: Diccionario con estadísticas de riesgos
    """
    riesgos = get_risks_for_service(service)

    if not riesgos:
        return {
            'total': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'avg_level': 0,
            'max_level': 0
        }

    high_count = len([r for r in riesgos if r.clasificacion_efectiva in ['ALTO', 'MUY_ALTO']])
    medium_count = len([r for r in riesgos if r.clasificacion_efectiva == 'MEDIO'])
    low_count = len([r for r in riesgos if r.clasificacion_efectiva in ['BAJO', 'MUY_BAJO']])

    niveles = [float(r.nivel_riesgo_efectivo or 0) for r in riesgos]
    avg_level = sum(niveles) / len(niveles) if niveles else 0
    max_level = max(niveles) if niveles else 0

    return {
        'total': len(riesgos),
        'high_count': high_count,
        'medium_count': medium_count,
        'low_count': low_count,
        'avg_level': round(avg_level, 2),
        'max_level': round(max_level, 2)
    }


# ==================== VISTAS DE RIESGOS POR SERVICIO ====================

@services_bp.route('/riesgos-por-servicio')
@login_required
def risks_by_service():
    """Vista general de riesgos agrupados por servicio"""

    # Obtener todos los servicios activos
    services = Service.query.filter_by(status=ServiceStatus.ACTIVE).all()

    # Calcular estadísticas de riesgos para cada servicio
    services_with_risks = []
    total_risks = 0
    services_with_high_risks = 0
    total_avg_risk = []

    for service in services:
        stats = calculate_service_risk_stats(service)

        if stats['total'] > 0:
            services_with_risks.append({
                'service': service,
                'stats': stats
            })
            total_risks += stats['total']

            if stats['high_count'] > 0:
                services_with_high_risks += 1

            total_avg_risk.append(stats['avg_level'])

    # Ordenar por número de riesgos altos/muy altos
    services_with_risks.sort(key=lambda x: x['stats']['high_count'], reverse=True)

    # Estadísticas generales
    general_stats = {
        'total_services': len(services_with_risks),
        'total_risks': total_risks,
        'services_with_high_risks': services_with_high_risks,
        'avg_risk_level': round(sum(total_avg_risk) / len(total_avg_risk), 2) if total_avg_risk else 0,
        'services_without_risks': len(services) - len(services_with_risks)
    }

    return render_template(
        'services/risks_by_service.html',
        services_with_risks=services_with_risks,
        stats=general_stats
    )


@services_bp.route('/<int:service_id>/riesgos')
@login_required
def service_risks_detail(service_id):
    """Vista detallada de riesgos de un servicio específico"""

    service = Service.query.get_or_404(service_id)
    riesgos = get_risks_for_service(service)

    # Obtener umbral de riesgo de la evaluación activa
    from app.risks.models import TratamientoRiesgo, EvaluacionRiesgo
    evaluacion_activa = EvaluacionRiesgo.query.filter(
        EvaluacionRiesgo.estado.in_(['en_curso', 'completada', 'aprobada'])
    ).order_by(EvaluacionRiesgo.created_at.desc()).first()

    umbral = float(evaluacion_activa.umbral_riesgo_objetivo or 50.0) if evaluacion_activa else 50.0

    # Clasificar riesgos por nivel
    sin_tratamiento = []
    a_tratar = []
    altos_muy_altos = []
    medios = []
    bajos = []

    for riesgo in riesgos:
        # Verificar si tiene tratamiento
        tratamiento = TratamientoRiesgo.query.filter_by(
            riesgo_id=riesgo.id
        ).order_by(TratamientoRiesgo.created_at.desc()).first()

        # Clasificar sin tratamiento
        if not tratamiento or tratamiento.estado == 'planificado':
            sin_tratamiento.append(riesgo)

        # Clasificar riesgos a tratar (superan umbral)
        nivel = float(riesgo.nivel_riesgo_efectivo or 0)
        if nivel > umbral:
            a_tratar.append(riesgo)

        # Clasificar por nivel de riesgo efectivo
        if nivel >= 50:  # Alto/Muy Alto
            altos_muy_altos.append(riesgo)
        elif nivel >= 25:  # Medio
            medios.append(riesgo)
        else:  # Bajo/Muy Bajo
            bajos.append(riesgo)

    # Construir estadísticas
    stats = {
        'total': len(riesgos),
        'sin_tratamiento': sin_tratamiento,
        'a_tratar': a_tratar,
        'altos_muy_altos': altos_muy_altos,
        'medios': medios,
        'bajos': bajos,
        'umbral': umbral
    }

    return render_template(
        'services/service_risks_detail.html',
        service=service,
        stats=stats
    )
