"""
Blueprint para gestión de incidentes de seguridad
ISO 27001:2023 - Controles 5.24, 5.25, 5.26, 5.27, 5.28
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import (
    Incident, IncidentCategory, IncidentSeverity, IncidentPriority,
    IncidentStatus, IncidentSource, DetectionMethod,
    IncidentTimeline, ActionType, IncidentAction, ActionStatus,
    IncidentEvidence, EvidenceType, IncidentNotification, NotificationType,
    IncidentAsset, Asset, User, db
)
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func
import hashlib
import os
from werkzeug.utils import secure_filename

incidents_bp = Blueprint('incidents', __name__, url_prefix='/incidents')

# Configuración de uploads
UPLOAD_FOLDER = 'uploads/incidents'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'log', 'pcap', 'zip'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_file_hash(file_path):
    """Calcula SHA-256 hash de un archivo para integridad"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


# ============================================================================
# VISTAS PRINCIPALES
# ============================================================================

@incidents_bp.route('/')
@login_required
def index():
    """Dashboard de incidentes"""
    # Filtros
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    severity_filter = request.args.get('severity')
    search = request.args.get('search', '')

    # Query base
    query = Incident.query

    # Aplicar filtros
    if status_filter and status_filter != 'all':
        query = query.filter(Incident.status == IncidentStatus[status_filter])

    if category_filter and category_filter != 'all':
        query = query.filter(Incident.category == IncidentCategory[category_filter])

    if severity_filter and severity_filter != 'all':
        query = query.filter(Incident.severity == IncidentSeverity[severity_filter])

    if search:
        query = query.filter(
            or_(
                Incident.incident_number.ilike(f'%{search}%'),
                Incident.title.ilike(f'%{search}%'),
                Incident.description.ilike(f'%{search}%')
            )
        )

    # Ordenar y paginar
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    incidents_pagination = query.order_by(Incident.reported_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Estadísticas rápidas
    stats = {
        'total': Incident.query.count(),
        'open': Incident.query.filter(Incident.status.in_([
            IncidentStatus.NEW, IncidentStatus.EVALUATING,
            IncidentStatus.CONFIRMED, IncidentStatus.IN_PROGRESS
        ])).count(),
        'critical': Incident.query.filter(Incident.severity == IncidentSeverity.CRITICAL).count(),
        'this_month': Incident.query.filter(
            Incident.reported_date >= datetime.utcnow().replace(day=1)
        ).count()
    }

    return render_template('incidents/index.html',
                          incidents=incidents_pagination.items,
                          pagination=incidents_pagination,
                          stats=stats,
                          IncidentStatus=IncidentStatus,
                          IncidentCategory=IncidentCategory,
                          IncidentSeverity=IncidentSeverity)


@incidents_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """Crear/reportar nuevo incidente"""
    if request.method == 'POST':
        try:
            # Generar número de incidente
            incident_number = Incident.generate_incident_number()

            # Crear incidente
            incident = Incident(
                incident_number=incident_number,
                title=request.form['title'],
                description=request.form['description'],
                category=IncidentCategory[request.form['category']],
                severity=IncidentSeverity[request.form['severity']],
                priority=IncidentPriority[request.form['priority']],
                status=IncidentStatus.NEW,
                discovery_date=datetime.strptime(request.form['discovery_date'], '%Y-%m-%dT%H:%M'),
                reported_date=datetime.utcnow(),
                reported_by_id=current_user.id,
                source=IncidentSource[request.form.get('source', 'UNKNOWN')],
                detection_method=DetectionMethod[request.form['detection_method']],
                detection_details=request.form.get('detection_details'),
                impact_confidentiality=request.form.get('impact_confidentiality') == 'on',
                impact_integrity=request.form.get('impact_integrity') == 'on',
                impact_availability=request.form.get('impact_availability') == 'on',
                created_by_id=current_user.id
            )

            # Asignar automáticamente si se especifica
            assigned_to_id = request.form.get('assigned_to_id')
            if assigned_to_id:
                incident.assigned_to_id = int(assigned_to_id)

            db.session.add(incident)
            db.session.flush()  # Para obtener el ID

            # Agregar activos afectados
            affected_asset_ids = request.form.getlist('affected_assets[]')
            for asset_id in affected_asset_ids:
                if asset_id:
                    incident_asset = IncidentAsset(
                        incident_id=incident.id,
                        asset_id=int(asset_id)
                    )
                    db.session.add(incident_asset)

            # Registrar evento de creación en timeline
            timeline_event = IncidentTimeline(
                incident_id=incident.id,
                timestamp=datetime.utcnow(),
                action_type=ActionType.CREATED,
                description=f"Incidente creado por {current_user.name}",
                user_id=current_user.id
            )
            db.session.add(timeline_event)

            db.session.commit()

            flash(f'Incidente {incident.incident_number} reportado correctamente', 'success')
            return redirect(url_for('incidents.view', id=incident.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear incidente: {str(e)}', 'error')

    # GET: Mostrar formulario
    users = User.query.filter_by(is_active=True).all()
    assets = Asset.query.all()

    return render_template('incidents/create.html',
                          users=users,
                          assets=assets,
                          IncidentCategory=IncidentCategory,
                          IncidentSeverity=IncidentSeverity,
                          IncidentPriority=IncidentPriority,
                          IncidentSource=IncidentSource,
                          DetectionMethod=DetectionMethod)


@incidents_bp.route('/<int:id>')
@login_required
def view(id):
    """Ver detalle de incidente"""
    incident = Incident.query.get_or_404(id)

    # Obtener métricas
    metrics = {
        'response_time': incident.calculate_response_time(),
        'resolution_time': incident.calculate_resolution_time()
    }

    return render_template('incidents/view.html',
                          incident=incident,
                          metrics=metrics,
                          IncidentStatus=IncidentStatus)


@incidents_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar incidente"""
    incident = Incident.query.get_or_404(id)

    # Solo el asignado, reportador o admin pueden editar
    if not (current_user.id == incident.assigned_to_id or
            current_user.id == incident.reported_by_id or
            current_user.has_role('admin')):
        flash('No tienes permisos para editar este incidente', 'error')
        return redirect(url_for('incidents.view', id=id))

    if request.method == 'POST':
        try:
            old_status = incident.status

            # Actualizar campos
            incident.title = request.form['title']
            incident.description = request.form['description']
            incident.category = IncidentCategory[request.form['category']]
            incident.severity = IncidentSeverity[request.form['severity']]
            incident.priority = IncidentPriority[request.form['priority']]
            incident.source = IncidentSource[request.form.get('source', 'UNKNOWN')]
            incident.detection_method = DetectionMethod[request.form['detection_method']]
            incident.detection_details = request.form.get('detection_details')
            incident.impact_confidentiality = request.form.get('impact_confidentiality') == 'on'
            incident.impact_integrity = request.form.get('impact_integrity') == 'on'
            incident.impact_availability = request.form.get('impact_availability') == 'on'
            incident.root_cause = request.form.get('root_cause')
            incident.contributing_factors = request.form.get('contributing_factors')
            incident.resolution = request.form.get('resolution')
            incident.lessons_learned = request.form.get('lessons_learned')
            incident.updated_by_id = current_user.id

            # Registrar cambio en timeline
            timeline_event = IncidentTimeline(
                incident_id=incident.id,
                timestamp=datetime.utcnow(),
                action_type=ActionType.COMMENT,
                description=f"Incidente actualizado por {current_user.name}",
                user_id=current_user.id
            )
            db.session.add(timeline_event)

            db.session.commit()
            flash('Incidente actualizado correctamente', 'success')
            return redirect(url_for('incidents.view', id=id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar incidente: {str(e)}', 'error')

    users = User.query.filter_by(is_active=True).all()
    assets = Asset.query.all()

    return render_template('incidents/edit.html',
                          incident=incident,
                          users=users,
                          assets=assets,
                          IncidentCategory=IncidentCategory,
                          IncidentSeverity=IncidentSeverity,
                          IncidentPriority=IncidentPriority,
                          IncidentSource=IncidentSource,
                          DetectionMethod=DetectionMethod)


# ============================================================================
# GESTIÓN DE ESTADO
# ============================================================================

@incidents_bp.route('/<int:id>/status', methods=['POST'])
@login_required
def change_status(id):
    """Cambiar estado del incidente"""
    incident = Incident.query.get_or_404(id)

    try:
        new_status = IncidentStatus[request.form['status']]
        old_status = incident.status
        comment = request.form.get('comment', '')

        incident.status = new_status
        incident.updated_by_id = current_user.id

        # Actualizar fechas según el estado
        if new_status == IncidentStatus.CONTAINED and not incident.containment_date:
            incident.containment_date = datetime.utcnow()
        elif new_status == IncidentStatus.RESOLVED and not incident.resolution_date:
            incident.resolution_date = datetime.utcnow()
        elif new_status == IncidentStatus.CLOSED and not incident.closure_date:
            incident.closure_date = datetime.utcnow()

        # Registrar en timeline
        description = f"Estado cambiado de {old_status.value} a {new_status.value}"
        if comment:
            description += f". Comentario: {comment}"

        timeline_event = IncidentTimeline(
            incident_id=incident.id,
            timestamp=datetime.utcnow(),
            action_type=ActionType.STATUS_CHANGE,
            description=description,
            details=comment,
            user_id=current_user.id
        )
        db.session.add(timeline_event)

        db.session.commit()
        flash(f'Estado actualizado a {new_status.value}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar estado: {str(e)}', 'error')

    return redirect(url_for('incidents.view', id=id))


@incidents_bp.route('/<int:id>/assign', methods=['POST'])
@login_required
def assign(id):
    """Asignar incidente a un usuario"""
    incident = Incident.query.get_or_404(id)

    try:
        user_id = request.form.get('user_id')
        if user_id:
            user = User.query.get(int(user_id))
            old_assigned = incident.assigned_to

            incident.assigned_to_id = user.id
            incident.updated_by_id = current_user.id

            # Registrar en timeline
            description = f"Incidente asignado a {user.name}"
            if old_assigned:
                description = f"Incidente reasignado de {old_assigned.name} a {user.name}"

            timeline_event = IncidentTimeline(
                incident_id=incident.id,
                timestamp=datetime.utcnow(),
                action_type=ActionType.ASSIGNED,
                description=description,
                user_id=current_user.id
            )
            db.session.add(timeline_event)

            db.session.commit()
            flash(f'Incidente asignado a {user.name}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al asignar incidente: {str(e)}', 'error')

    return redirect(url_for('incidents.view', id=id))


# ============================================================================
# TIMELINE Y COMENTARIOS
# ============================================================================

@incidents_bp.route('/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    """Agregar comentario al incidente"""
    incident = Incident.query.get_or_404(id)

    try:
        comment = request.form.get('comment')
        if comment:
            timeline_event = IncidentTimeline(
                incident_id=incident.id,
                timestamp=datetime.utcnow(),
                action_type=ActionType.COMMENT,
                description=comment,
                user_id=current_user.id
            )
            db.session.add(timeline_event)
            db.session.commit()
            flash('Comentario agregado', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar comentario: {str(e)}', 'error')

    return redirect(url_for('incidents.view', id=id))


# ============================================================================
# ACCIONES CORRECTIVAS
# ============================================================================

@incidents_bp.route('/<int:id>/actions', methods=['GET', 'POST'])
@login_required
def actions(id):
    """Gestionar acciones correctivas"""
    incident = Incident.query.get_or_404(id)

    if request.method == 'POST':
        try:
            action = IncidentAction(
                incident_id=incident.id,
                action_type=request.form.get('action_type', 'Correctiva'),
                description=request.form['description'],
                responsible_id=int(request.form['responsible_id']) if request.form.get('responsible_id') else None,
                due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d').date() if request.form.get('due_date') else None,
                status=ActionStatus.PENDING
            )

            db.session.add(action)

            # Registrar en timeline
            timeline_event = IncidentTimeline(
                incident_id=incident.id,
                timestamp=datetime.utcnow(),
                action_type=ActionType.ACTION_ADDED,
                description=f"Nueva acción agregada: {action.description[:50]}...",
                user_id=current_user.id
            )
            db.session.add(timeline_event)

            db.session.commit()
            flash('Acción creada correctamente', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear acción: {str(e)}', 'error')

        return redirect(url_for('incidents.view', id=id))

    users = User.query.filter_by(is_active=True).all()
    return render_template('incidents/actions.html',
                          incident=incident,
                          users=users,
                          ActionStatus=ActionStatus)


@incidents_bp.route('/actions/<int:action_id>/complete', methods=['POST'])
@login_required
def complete_action(action_id):
    """Marcar acción como completada"""
    action = IncidentAction.query.get_or_404(action_id)

    try:
        action.status = ActionStatus.COMPLETED
        action.completion_date = datetime.utcnow().date()
        action.notes = request.form.get('notes')

        # Registrar en timeline
        timeline_event = IncidentTimeline(
            incident_id=action.incident_id,
            timestamp=datetime.utcnow(),
            action_type=ActionType.COMMENT,
            description=f"Acción completada: {action.description[:50]}...",
            user_id=current_user.id
        )
        db.session.add(timeline_event)

        db.session.commit()
        flash('Acción marcada como completada', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al completar acción: {str(e)}', 'error')

    return redirect(url_for('incidents.view', id=action.incident_id))


# ============================================================================
# EVIDENCIAS
# ============================================================================

@incidents_bp.route('/<int:id>/evidences', methods=['GET', 'POST'])
@login_required
def evidences(id):
    """Gestionar evidencias del incidente"""
    incident = Incident.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Procesar archivo si existe
            file_path = None
            file_hash = None
            file_size = None
            file_name = None

            if 'evidence_file' in request.files:
                file = request.files['evidence_file']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Crear directorio si no existe
                    upload_dir = os.path.join(UPLOAD_FOLDER, str(incident.id))
                    os.makedirs(upload_dir, exist_ok=True)

                    # Guardar archivo con timestamp
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                    file_name = f"{timestamp}_{filename}"
                    file_path = os.path.join(upload_dir, file_name)
                    file.save(file_path)

                    # Calcular hash
                    file_hash = calculate_file_hash(file_path)
                    file_size = os.path.getsize(file_path)

            # Crear evidencia
            evidence = IncidentEvidence(
                incident_id=incident.id,
                evidence_type=EvidenceType[request.form['evidence_type']],
                description=request.form['description'],
                file_path=file_path,
                file_name=file_name,
                file_size=file_size,
                hash_value=file_hash,
                collected_by_id=current_user.id,
                collection_date=datetime.utcnow(),
                chain_of_custody=f"Recopilado por {current_user.name} el {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
                notes=request.form.get('notes')
            )

            db.session.add(evidence)

            # Registrar en timeline
            timeline_event = IncidentTimeline(
                incident_id=incident.id,
                timestamp=datetime.utcnow(),
                action_type=ActionType.EVIDENCE_ADDED,
                description=f"Nueva evidencia agregada: {evidence.evidence_type.value}",
                user_id=current_user.id
            )
            db.session.add(timeline_event)

            db.session.commit()
            flash('Evidencia agregada correctamente', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar evidencia: {str(e)}', 'error')

        return redirect(url_for('incidents.view', id=id))

    return render_template('incidents/evidences.html',
                          incident=incident,
                          EvidenceType=EvidenceType)


# ============================================================================
# REPORTES Y MÉTRICAS
# ============================================================================

@incidents_bp.route('/reports')
@login_required
def reports():
    """Dashboard de reportes y métricas"""
    # Métricas generales
    total_incidents = Incident.query.count()

    # Incidentes por estado
    by_status = db.session.query(
        Incident.status, func.count(Incident.id)
    ).group_by(Incident.status).all()

    # Incidentes por categoría
    by_category = db.session.query(
        Incident.category, func.count(Incident.id)
    ).group_by(Incident.category).all()

    # Incidentes por gravedad
    by_severity = db.session.query(
        Incident.severity, func.count(Incident.id)
    ).group_by(Incident.severity).all()

    # Tendencia mensual (últimos 6 meses)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    monthly_trend = db.session.query(
        func.date_trunc('month', Incident.reported_date).label('month'),
        func.count(Incident.id)
    ).filter(
        Incident.reported_date >= six_months_ago
    ).group_by('month').order_by('month').all()

    # Métricas de tiempo (MTTD, MTTR, etc.)
    resolved_incidents = Incident.query.filter(
        Incident.resolution_date.isnot(None)
    ).all()

    if resolved_incidents:
        avg_resolution_time = sum([
            i.calculate_resolution_time() for i in resolved_incidents if i.calculate_resolution_time()
        ]) / len([i for i in resolved_incidents if i.calculate_resolution_time()])
    else:
        avg_resolution_time = 0

    return render_template('incidents/reports.html',
                          total_incidents=total_incidents,
                          by_status=by_status,
                          by_category=by_category,
                          by_severity=by_severity,
                          monthly_trend=monthly_trend,
                          avg_resolution_time=avg_resolution_time)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@incidents_bp.route('/api/stats')
@login_required
def api_stats():
    """API para obtener estadísticas"""
    stats = {
        'total': Incident.query.count(),
        'new': Incident.query.filter_by(status=IncidentStatus.NEW).count(),
        'in_progress': Incident.query.filter_by(status=IncidentStatus.IN_PROGRESS).count(),
        'resolved': Incident.query.filter_by(status=IncidentStatus.RESOLVED).count(),
        'closed': Incident.query.filter_by(status=IncidentStatus.CLOSED).count(),
        'critical': Incident.query.filter_by(severity=IncidentSeverity.CRITICAL).count()
    }
    return jsonify(stats)


@incidents_bp.route('/api/<int:id>')
@login_required
def api_get(id):
    """API para obtener un incidente"""
    incident = Incident.query.get_or_404(id)
    return jsonify(incident.to_dict())
