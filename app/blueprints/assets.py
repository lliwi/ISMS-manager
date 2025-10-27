"""
Blueprint para Gestión de Activos/Inventario
Control 5.9 - Inventario de información y otros activos asociados
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import (
    db, User, Asset, AssetCategory, ClassificationLevel, CIALevel, AssetStatus,
    AssetRelationship, RelationshipType, AssetLifecycleEvent, EventType, AssetControl
)
from datetime import datetime
from sqlalchemy import or_, and_, func

assets_bp = Blueprint('assets', __name__)


@assets_bp.route('/')
@login_required
def index():
    """Lista de activos con filtros y búsqueda"""
    # Parámetros de búsqueda y filtrado
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    classification = request.args.get('classification', '')
    status = request.args.get('status', '')
    owner_id = request.args.get('owner_id', '')

    # Query base
    query = Asset.query

    # Aplicar filtros
    if search:
        query = query.filter(
            or_(
                Asset.name.ilike(f'%{search}%'),
                Asset.asset_code.ilike(f'%{search}%'),
                Asset.description.ilike(f'%{search}%')
            )
        )

    if category:
        query = query.filter(Asset.category == AssetCategory[category])

    if classification:
        query = query.filter(Asset.classification == ClassificationLevel[classification])

    if status:
        query = query.filter(Asset.status == AssetStatus[status])

    if owner_id:
        query = query.filter(Asset.owner_id == owner_id)

    # Ordenar y obtener resultados
    assets = query.order_by(Asset.created_at.desc()).all()

    # Estadísticas para el dashboard
    stats = {
        'total': Asset.query.count(),
        'by_category': db.session.query(
            Asset.category, func.count(Asset.id)
        ).group_by(Asset.category).all(),
        'by_status': db.session.query(
            Asset.status, func.count(Asset.id)
        ).group_by(Asset.status).all(),
        'critical': Asset.query.filter(
            or_(
                Asset.confidentiality_level == CIALevel.CRITICAL,
                Asset.integrity_level == CIALevel.CRITICAL,
                Asset.availability_level == CIALevel.CRITICAL
            )
        ).count()
    }

    # Usuarios para filtros
    users = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()

    return render_template(
        'assets/index.html',
        assets=assets,
        stats=stats,
        users=users,
        AssetCategory=AssetCategory,
        ClassificationLevel=ClassificationLevel,
        AssetStatus=AssetStatus
    )


@assets_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """Crear nuevo activo"""
    if not current_user.can_access('assets'):
        flash('No tienes permisos para crear activos', 'error')
        return redirect(url_for('assets.index'))

    if request.method == 'POST':
        try:
            # Generar código único de activo
            category_prefix = {
                'HARDWARE': 'HW',
                'SOFTWARE': 'SW',
                'INFORMATION': 'INF',
                'SERVICES': 'SRV',
                'PEOPLE': 'PER',
                'FACILITIES': 'FAC'
            }
            category = request.form['category']
            prefix = category_prefix.get(category, 'AST')

            # Obtener el último número para esta categoría
            last_asset = Asset.query.filter(
                Asset.asset_code.like(f'{prefix}-%')
            ).order_by(Asset.asset_code.desc()).first()

            if last_asset:
                last_num = int(last_asset.asset_code.split('-')[1])
                new_num = last_num + 1
            else:
                new_num = 1

            asset_code = f"{prefix}-{new_num:05d}"

            # Crear activo
            asset = Asset(
                asset_code=asset_code,
                name=request.form['name'],
                description=request.form.get('description'),
                category=AssetCategory[category],
                asset_type_id=int(request.form['asset_type_id']) if request.form.get('asset_type_id') else None,
                owner_id=int(request.form['owner_id']),
                custodian_id=int(request.form['custodian_id']) if request.form.get('custodian_id') else None,
                physical_location=request.form.get('physical_location'),
                logical_location=request.form.get('logical_location'),
                department=request.form.get('department'),
                classification=ClassificationLevel[request.form['classification']],
                confidentiality_level=CIALevel[request.form['confidentiality_level']],
                integrity_level=CIALevel[request.form['integrity_level']],
                availability_level=CIALevel[request.form['availability_level']],
                manufacturer=request.form.get('manufacturer'),
                model=request.form.get('model'),
                serial_number=request.form.get('serial_number'),
                version=request.form.get('version'),
                acquisition_date=datetime.strptime(request.form['acquisition_date'], '%Y-%m-%d').date() if request.form.get('acquisition_date') else None,
                purchase_cost=float(request.form['purchase_cost']) if request.form.get('purchase_cost') else None,
                current_value=float(request.form['current_value']) if request.form.get('current_value') else None,
                tags=request.form.get('tags'),
                acceptable_use_policy=request.form.get('acceptable_use_policy'),
                handling_requirements=request.form.get('handling_requirements'),
                notes=request.form.get('notes'),
                status=AssetStatus.ACTIVE,
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )

            # Calcular valores automáticamente o usar valores manuales
            # Si el usuario proporciona valores manuales, usarlos; sino, calcular automáticamente
            if request.form.get('business_value') and request.form.get('business_value').strip():
                asset.business_value = int(request.form['business_value'])
            else:
                asset.business_value = asset.calculate_business_value()

            if request.form.get('criticality') and request.form.get('criticality').strip():
                asset.criticality = int(request.form['criticality'])
            else:
                asset.criticality = asset.calculate_criticality()

            db.session.add(asset)
            db.session.flush()  # Para obtener el ID del activo

            # Registrar evento de creación
            event = AssetLifecycleEvent(
                asset_id=asset.id,
                event_type=EventType.CREATED,
                description=f'Activo creado: {asset.name}',
                performed_by_id=current_user.id
            )
            db.session.add(event)

            db.session.commit()

            flash(f'Activo {asset.asset_code} creado correctamente', 'success')
            return redirect(url_for('assets.view', id=asset.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el activo: {str(e)}', 'error')
            return redirect(url_for('assets.create'))

    # GET request - mostrar formulario
    users = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()
    return render_template(
        'assets/create.html',
        users=users,
        AssetCategory=AssetCategory,
        ClassificationLevel=ClassificationLevel,
        CIALevel=CIALevel
    )


@assets_bp.route('/<int:id>')
@login_required
def view(id):
    """Ver detalles de un activo"""
    asset = Asset.query.get_or_404(id)

    # Obtener relaciones
    relationships = asset.get_all_relationships()

    # Obtener controles aplicados
    controls = AssetControl.query.filter_by(asset_id=asset.id).all()

    # Obtener historial de eventos
    events = AssetLifecycleEvent.query.filter_by(asset_id=asset.id).order_by(
        AssetLifecycleEvent.event_date.desc()
    ).limit(20).all()

    # Calcular puntuación de riesgo
    risk_score = asset.calculate_risk_score()

    return render_template(
        'assets/view.html',
        asset=asset,
        relationships=relationships,
        controls=controls,
        events=events,
        risk_score=risk_score
    )


@assets_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar activo existente"""
    asset = Asset.query.get_or_404(id)

    if not current_user.can_access('assets'):
        flash('No tienes permisos para editar activos', 'error')
        return redirect(url_for('assets.view', id=id))

    if request.method == 'POST':
        try:
            # Guardar valores anteriores para el evento
            old_values = {
                'classification': asset.classification,
                'owner': asset.owner.full_name if asset.owner else None,
                'status': asset.status
            }

            # Actualizar campos
            asset.name = request.form['name']
            asset.description = request.form.get('description')
            asset.asset_type_id = int(request.form['asset_type_id']) if request.form.get('asset_type_id') else None
            asset.owner_id = int(request.form['owner_id'])
            asset.custodian_id = int(request.form['custodian_id']) if request.form.get('custodian_id') else None
            asset.physical_location = request.form.get('physical_location')
            asset.logical_location = request.form.get('logical_location')
            asset.department = request.form.get('department')
            asset.classification = ClassificationLevel[request.form['classification']]
            asset.confidentiality_level = CIALevel[request.form['confidentiality_level']]
            asset.integrity_level = CIALevel[request.form['integrity_level']]
            asset.availability_level = CIALevel[request.form['availability_level']]
            asset.manufacturer = request.form.get('manufacturer')
            asset.model = request.form.get('model')
            asset.serial_number = request.form.get('serial_number')
            asset.version = request.form.get('version')
            asset.status = AssetStatus[request.form['status']]
            asset.tags = request.form.get('tags')
            asset.acceptable_use_policy = request.form.get('acceptable_use_policy')
            asset.handling_requirements = request.form.get('handling_requirements')
            asset.notes = request.form.get('notes')
            asset.purchase_cost = float(request.form['purchase_cost']) if request.form.get('purchase_cost') else None
            asset.current_value = float(request.form['current_value']) if request.form.get('current_value') else None
            asset.updated_by_id = current_user.id

            # Calcular valores automáticamente o usar valores manuales
            if request.form.get('business_value') and request.form.get('business_value').strip():
                asset.business_value = int(request.form['business_value'])
            else:
                asset.business_value = asset.calculate_business_value()

            if request.form.get('criticality') and request.form.get('criticality').strip():
                asset.criticality = int(request.form['criticality'])
            else:
                asset.criticality = asset.calculate_criticality()

            # Registrar evento de modificación
            changes = []
            if old_values['classification'] != asset.classification:
                changes.append(f"Clasificación: {old_values['classification'].value} → {asset.classification.value}")
            if old_values['status'] != asset.status:
                changes.append(f"Estado: {old_values['status'].value} → {asset.status.value}")

            event = AssetLifecycleEvent(
                asset_id=asset.id,
                event_type=EventType.MODIFIED,
                description=f'Activo modificado: {", ".join(changes) if changes else "Actualización general"}',
                performed_by_id=current_user.id
            )
            db.session.add(event)

            db.session.commit()

            flash('Activo actualizado correctamente', 'success')
            return redirect(url_for('assets.view', id=asset.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el activo: {str(e)}', 'error')

    users = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()
    return render_template(
        'assets/edit.html',
        asset=asset,
        users=users,
        ClassificationLevel=ClassificationLevel,
        CIALevel=CIALevel,
        AssetStatus=AssetStatus
    )


@assets_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Eliminar activo (cambiar a estado DISPOSED)"""
    asset = Asset.query.get_or_404(id)

    if not current_user.can_access('assets'):
        flash('No tienes permisos para eliminar activos', 'error')
        return redirect(url_for('assets.view', id=id))

    try:
        # No eliminar físicamente, cambiar estado
        asset.status = AssetStatus.DISPOSED
        asset.updated_by_id = current_user.id

        # Registrar evento
        event = AssetLifecycleEvent(
            asset_id=asset.id,
            event_type=EventType.DISPOSED,
            description=f'Activo eliminado/dado de baja',
            performed_by_id=current_user.id
        )
        db.session.add(event)

        db.session.commit()

        flash('Activo eliminado correctamente', 'success')
        return redirect(url_for('assets.index'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el activo: {str(e)}', 'error')
        return redirect(url_for('assets.view', id=id))


@assets_bp.route('/<int:id>/relationships', methods=['GET', 'POST'])
@login_required
def manage_relationships(id):
    """Gestionar relaciones del activo"""
    asset = Asset.query.get_or_404(id)

    if request.method == 'POST':
        try:
            target_asset_id = int(request.form['target_asset_id'])
            relationship_type = RelationshipType[request.form['relationship_type']]
            description = request.form.get('description')
            criticality = int(request.form.get('criticality', 5))

            # Crear relación
            relationship = AssetRelationship(
                source_asset_id=asset.id,
                target_asset_id=target_asset_id,
                relationship_type=relationship_type,
                description=description,
                criticality=criticality,
                created_by_id=current_user.id
            )

            db.session.add(relationship)
            db.session.commit()

            flash('Relación creada correctamente', 'success')
            return redirect(url_for('assets.view', id=asset.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la relación: {str(e)}', 'error')

    # Obtener activos disponibles para relacionar
    available_assets = Asset.query.filter(
        Asset.id != asset.id,
        Asset.status == AssetStatus.ACTIVE
    ).order_by(Asset.name).all()

    return render_template(
        'assets/relationships.html',
        asset=asset,
        available_assets=available_assets,
        RelationshipType=RelationshipType
    )


@assets_bp.route('/relationships/<int:id>/delete', methods=['POST'])
@login_required
def delete_relationship(id):
    """Eliminar relación entre activos"""
    relationship = AssetRelationship.query.get_or_404(id)
    asset_id = relationship.source_asset_id

    try:
        db.session.delete(relationship)
        db.session.commit()
        flash('Relación eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la relación: {str(e)}', 'error')

    return redirect(url_for('assets.view', id=asset_id))


@assets_bp.route('/<int:id>/controls', methods=['GET', 'POST'])
@login_required
def manage_controls(id):
    """Gestionar controles aplicados al activo"""
    asset = Asset.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Obtener los controles seleccionados (puede ser múltiple)
            selected_control_ids = request.form.getlist('selected_controls')

            if not selected_control_ids:
                flash('Debe seleccionar al menos un control', 'warning')
                return redirect(url_for('assets.manage_controls', id=asset.id))

            # Obtener datos comunes del formulario
            implementation_status = request.form.get('implementation_status', 'Planificado')
            effectiveness = int(request.form.get('effectiveness', 5)) if request.form.get('effectiveness') else None
            implementation_description = request.form.get('implementation_description')
            evidence = request.form.get('evidence')
            responsible_id = int(request.form['responsible_id']) if request.form.get('responsible_id') else None

            from models import SOAControl
            controls_added = 0

            for soa_control_id in selected_control_ids:
                # Verificar si el control ya está aplicado al activo
                soa_control = SOAControl.query.get(soa_control_id)
                if not soa_control:
                    continue

                existing = AssetControl.query.filter_by(
                    asset_id=asset.id,
                    control_code=soa_control.control_id
                ).first()

                if existing:
                    continue  # Saltar si ya existe

                control = AssetControl(
                    asset_id=asset.id,
                    control_code=soa_control.control_id,
                    control_name=soa_control.title,
                    implementation_status=implementation_status,
                    effectiveness=effectiveness,
                    implementation_description=implementation_description,
                    evidence=evidence,
                    responsible_id=responsible_id
                )

                db.session.add(control)
                controls_added += 1

                # Registrar evento
                event = AssetLifecycleEvent(
                    asset_id=asset.id,
                    event_type=EventType.CONTROL_APPLIED,
                    description=f'Control aplicado: {control.control_code} - {control.control_name}',
                    performed_by_id=current_user.id
                )
                db.session.add(event)

            db.session.commit()

            if controls_added > 0:
                flash(f'{controls_added} control(es) aplicado(s) correctamente', 'success')
            else:
                flash('Todos los controles seleccionados ya están aplicados a este activo', 'info')

            return redirect(url_for('assets.view', id=asset.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al aplicar controles: {str(e)}', 'error')

    # Obtener controles del SOA activo
    from models import SOAVersion, SOAControl
    current_soa = SOAVersion.get_current_version()
    soa_controls = []
    if current_soa:
        soa_controls = SOAControl.query.filter_by(
            soa_version_id=current_soa.id,
            applicability_status='aplicable'
        ).order_by(SOAControl.control_id).all()

    users = User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()
    return render_template(
        'assets/controls.html',
        asset=asset,
        users=users,
        soa_controls=soa_controls
    )


@assets_bp.route('/controls/<int:id>/delete', methods=['POST'])
@login_required
def delete_control(id):
    """Eliminar control aplicado"""
    control = AssetControl.query.get_or_404(id)
    asset_id = control.asset_id

    try:
        # Registrar evento antes de eliminar
        event = AssetLifecycleEvent(
            asset_id=asset_id,
            event_type=EventType.CONTROL_REMOVED,
            description=f'Control eliminado: {control.control_code} - {control.control_name}',
            performed_by_id=current_user.id
        )
        db.session.add(event)

        db.session.delete(control)
        db.session.commit()
        flash('Control eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el control: {str(e)}', 'error')

    return redirect(url_for('assets.view', id=asset_id))


@assets_bp.route('/api/asset-types/<category>')
@login_required
def api_asset_types(category):
    """API para obtener tipos de activos filtrados por categoría"""
    from models import AssetType, AssetCategory

    try:
        # Convertir el string de categoría al enum
        category_enum = AssetCategory[category]

        # Obtener tipos activos para esta categoría
        asset_types = AssetType.query.filter_by(
            category=category_enum,
            is_active=True
        ).order_by(AssetType.order, AssetType.name).all()

        return jsonify([
            {
                'id': at.id,
                'code': at.code,
                'name': at.name,
                'description': at.description,
                'icon': at.icon,
                'color': at.color
            }
            for at in asset_types
        ])
    except KeyError:
        return jsonify({'error': 'Categoría inválida'}), 400


@assets_bp.route('/api/search')
@login_required
def api_search():
    """API para búsqueda de activos (usado en autocompletado)"""
    q = request.args.get('q', '')

    assets = Asset.query.filter(
        or_(
            Asset.name.ilike(f'%{q}%'),
            Asset.asset_code.ilike(f'%{q}%')
        ),
        Asset.status == AssetStatus.ACTIVE
    ).limit(10).all()

    return jsonify([
        {
            'id': asset.id,
            'code': asset.asset_code,
            'name': asset.name,
            'category': asset.category.value
        }
        for asset in assets
    ])


@assets_bp.route('/api/stats')
@login_required
def api_stats():
    """API para estadísticas del dashboard"""
    stats = {
        'total': Asset.query.count(),
        'active': Asset.query.filter_by(status=AssetStatus.ACTIVE).count(),
        'critical': Asset.query.filter(
            or_(
                Asset.confidentiality_level == CIALevel.CRITICAL,
                Asset.integrity_level == CIALevel.CRITICAL,
                Asset.availability_level == CIALevel.CRITICAL
            )
        ).count(),
        'by_category': [
            {'category': cat[0].value, 'count': cat[1]}
            for cat in db.session.query(
                Asset.category, func.count(Asset.id)
            ).group_by(Asset.category).all()
        ],
        'by_classification': [
            {'classification': cls[0].value, 'count': cls[1]}
            for cls in db.session.query(
                Asset.classification, func.count(Asset.id)
            ).group_by(Asset.classification).all()
        ]
    }

    return jsonify(stats)


@assets_bp.route('/export')
@login_required
def export():
    """Exportar inventario de activos a CSV"""
    import csv
    from io import StringIO
    from flask import make_response

    # Crear CSV en memoria
    si = StringIO()
    writer = csv.writer(si)

    # Cabeceras
    writer.writerow([
        'Código', 'Nombre', 'Categoría', 'Propietario', 'Clasificación',
        'Confidencialidad', 'Integridad', 'Disponibilidad', 'Valor',
        'Criticidad', 'Estado', 'Ubicación', 'Fecha Adquisición'
    ])

    # Datos
    assets = Asset.query.order_by(Asset.asset_code).all()
    for asset in assets:
        writer.writerow([
            asset.asset_code,
            asset.name,
            asset.category.value if asset.category else '',
            asset.owner.name if asset.owner else '',
            asset.classification.value if asset.classification else '',
            asset.confidentiality_level.value if asset.confidentiality_level else '',
            asset.integrity_level.value if asset.integrity_level else '',
            asset.availability_level.value if asset.availability_level else '',
            asset.business_value,
            asset.criticality,
            asset.status.value if asset.status else '',
            asset.physical_location or '',
            asset.acquisition_date.strftime('%Y-%m-%d') if asset.acquisition_date else ''
        ])

    # Crear respuesta
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=inventario_activos.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"

    return output


@assets_bp.route('/graph/test')
@login_required
def graph_test():
    """Página de prueba de D3.js"""
    return render_template('assets/graph_test.html')


@assets_bp.route('/graph')
@login_required
def graph():
    """Vista del grafo de relaciones entre activos"""
    # Obtener estadísticas para el panel
    total_assets = Asset.query.filter_by(status=AssetStatus.ACTIVE).count()
    total_relationships = AssetRelationship.query.count()

    # Obtener categorías y tipos de relación para filtros
    categories = [cat.value for cat in AssetCategory]
    relationship_types = [rt.value for rt in RelationshipType]

    return render_template('assets/graph.html',
                          total_assets=total_assets,
                          total_relationships=total_relationships,
                          categories=categories,
                          relationship_types=relationship_types)


@assets_bp.route('/api/graph-data')
@login_required
def graph_data():
    """
    API endpoint que devuelve datos del grafo en formato JSON para D3.js

    Parámetros de consulta:
    - category: Filtrar por categoría de activo
    - min_criticality: Criticidad mínima (1-10)
    - include_inactive: Incluir activos inactivos (true/false)
    - relationship_type: Filtrar por tipo de relación
    """
    # Obtener parámetros de filtrado
    category_filter = request.args.get('category', '')
    min_criticality = request.args.get('min_criticality', 0, type=int)
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    relationship_filter = request.args.get('relationship_type', '')

    print(f"🔍 Graph API llamado con filtros: category={category_filter}, criticality={min_criticality}, inactive={include_inactive}")

    # Query base para activos
    assets_query = Asset.query

    # Filtrar por estado
    if not include_inactive:
        assets_query = assets_query.filter_by(status=AssetStatus.ACTIVE)
        print(f"  → Filtrando solo activos ACTIVE")

    # Filtrar por categoría
    if category_filter:
        try:
            assets_query = assets_query.filter_by(category=AssetCategory[category_filter])
        except KeyError:
            pass

    # Filtrar por criticidad mínima
    if min_criticality > 0:
        assets_query = assets_query.filter(Asset.criticality >= min_criticality)

    assets = assets_query.all()
    asset_ids = {asset.id for asset in assets}

    print(f"  → Encontrados {len(assets)} activos")

    # Construir nodos
    nodes = []
    for asset in assets:
        nodes.append({
            'id': asset.id,
            'code': asset.asset_code,
            'name': asset.name,
            'category': asset.category.value if asset.category else 'Unknown',
            'classification': asset.classification.value if asset.classification else 'Internal',
            'criticality': asset.criticality or 5,
            'business_value': asset.business_value or 5,
            'status': asset.status.value if asset.status else 'Active',
            'owner': asset.owner.name if asset.owner else 'Sin asignar',
            'department': asset.department or '',
            'location': asset.physical_location or '',
            # Información CIA
            'confidentiality': asset.confidentiality_level.value if asset.confidentiality_level else 'Medio',
            'integrity': asset.integrity_level.value if asset.integrity_level else 'Medio',
            'availability': asset.availability_level.value if asset.availability_level else 'Medio'
        })

    # Query para relaciones
    relationships_query = AssetRelationship.query.filter(
        AssetRelationship.source_asset_id.in_(asset_ids),
        AssetRelationship.target_asset_id.in_(asset_ids)
    )

    # Filtrar por tipo de relación
    if relationship_filter:
        try:
            relationships_query = relationships_query.filter_by(
                relationship_type=RelationshipType[relationship_filter]
            )
        except KeyError:
            pass

    relationships = relationships_query.all()

    print(f"  → Encontradas {len(relationships)} relaciones")

    # Construir enlaces (links)
    links = []
    for rel in relationships:
        links.append({
            'source': rel.source_asset_id,
            'target': rel.target_asset_id,
            'type': rel.relationship_type.value if rel.relationship_type else 'USES',
            'criticality': rel.criticality or 5,
            'description': rel.description or ''
        })

    # Calcular estadísticas del grafo
    stats = {
        'total_nodes': len(nodes),
        'total_links': len(links),
        'avg_criticality': sum(n['criticality'] for n in nodes) / len(nodes) if nodes else 0,
        'categories': {},
        'orphan_nodes': 0  # Nodos sin relaciones
    }

    # Contar nodos por categoría
    for node in nodes:
        cat = node['category']
        stats['categories'][cat] = stats['categories'].get(cat, 0) + 1

    # Identificar nodos huérfanos
    connected_nodes = set()
    for link in links:
        connected_nodes.add(link['source'])
        connected_nodes.add(link['target'])
    stats['orphan_nodes'] = len(nodes) - len(connected_nodes)

    print(f"  → Devolviendo JSON con {len(nodes)} nodos y {len(links)} enlaces")

    return jsonify({
        'nodes': nodes,
        'links': links,
        'stats': stats
    })
