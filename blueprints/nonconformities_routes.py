"""
Blueprint para Gestión de No Conformidades - ISO 27001:2023
Control 10.2 - No conformidad y acciones correctivas
Control 10.1 - Mejora continua
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta
from models import (
    db, User, Audit, Asset,
    NonConformity, CorrectiveAction, NCTimeline, NCAsset, NCAttachment,
    NCOrigin, NCSeverity, NCStatus, RCAMethod, ActionType, ActionStatus,
    NCTimelineEventType
)
from werkzeug.utils import secure_filename
import os

nonconformities_bp = Blueprint('nonconformities', __name__)

# Configuración de uploads
UPLOAD_FOLDER = 'uploads/nonconformities'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@nonconformities_bp.route('/')
@login_required
def index():
    """Dashboard principal de no conformidades"""

    # Filtros desde query params
    status_filter = request.args.get('status', '')
    severity_filter = request.args.get('severity', '')
    origin_filter = request.args.get('origin', '')
    search = request.args.get('search', '')

    # Query base
    query = NonConformity.query

    # Aplicar filtros
    if status_filter:
        query = query.filter(NonConformity.status == NCStatus[status_filter])
    if severity_filter:
        query = query.filter(NonConformity.severity == NCSeverity[severity_filter])
    if origin_filter:
        query = query.filter(NonConformity.origin == NCOrigin[origin_filter])
    if search:
        query = query.filter(
            or_(
                NonConformity.title.ilike(f'%{search}%'),
                NonConformity.description.ilike(f'%{search}%'),
                NonConformity.nc_number.ilike(f'%{search}%')
            )
        )

    # Ordenar
    nonconformities = query.order_by(NonConformity.created_at.desc()).all()

    # KPIs básicos para el dashboard
    total_nc = NonConformity.query.count()
    open_nc = NonConformity.query.filter(NonConformity.status != NCStatus.CLOSED).count()
    critical_nc = NonConformity.query.filter(NonConformity.severity == NCSeverity.CRITICAL).count()
    overdue_nc = sum(1 for nc in nonconformities if nc.is_overdue())

    return render_template('nonconformities/index.html',
                         nonconformities=nonconformities,
                         total_nc=total_nc,
                         open_nc=open_nc,
                         critical_nc=critical_nc,
                         overdue_nc=overdue_nc,
                         NCStatus=NCStatus,
                         NCSeverity=NCSeverity,
                         NCOrigin=NCOrigin,
                         current_filters={
                             'status': status_filter,
                             'severity': severity_filter,
                             'origin': origin_filter,
                             'search': search
                         })


@nonconformities_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard con métricas y KPIs detallados"""

    # Métricas generales
    total_nc = NonConformity.query.count()
    open_nc = NonConformity.query.filter(NonConformity.status != NCStatus.CLOSED).count()
    closed_nc = NonConformity.query.filter(NonConformity.status == NCStatus.CLOSED).count()

    # Por severidad
    critical_nc = NonConformity.query.filter(NonConformity.severity == NCSeverity.CRITICAL).count()
    major_nc = NonConformity.query.filter(NonConformity.severity == NCSeverity.MAJOR).count()
    minor_nc = NonConformity.query.filter(NonConformity.severity == NCSeverity.MINOR).count()

    # Por origen
    nc_by_origin = db.session.query(
        NonConformity.origin,
        func.count(NonConformity.id)
    ).group_by(NonConformity.origin).all()

    # Por estado
    nc_by_status = db.session.query(
        NonConformity.status,
        func.count(NonConformity.id)
    ).group_by(NonConformity.status).all()

    # Tiempo promedio de resolución
    closed_ncs = NonConformity.query.filter(NonConformity.status == NCStatus.CLOSED).all()
    avg_resolution_time = sum(nc.calculate_resolution_time() or 0 for nc in closed_ncs) / len(closed_ncs) if closed_ncs else 0

    # NC recurrentes
    recurrent_nc = NonConformity.query.filter(NonConformity.is_recurrent == True).count()

    # NC vencidas
    overdue_nc = [nc for nc in NonConformity.query.filter(NonConformity.status != NCStatus.CLOSED).all() if nc.is_overdue()]

    # Tendencia últimos 6 meses
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    nc_trend = db.session.query(
        extract('year', NonConformity.reported_date).label('year'),
        extract('month', NonConformity.reported_date).label('month'),
        func.count(NonConformity.id).label('count')
    ).filter(
        NonConformity.reported_date >= six_months_ago
    ).group_by('year', 'month').order_by('year', 'month').all()

    # Top 5 controles más afectados
    # Necesitamos desempaquetar el JSON affected_controls
    all_controls = []
    for nc in NonConformity.query.all():
        if nc.affected_controls:
            all_controls.extend(nc.affected_controls)

    from collections import Counter
    top_controls = Counter(all_controls).most_common(5)

    return render_template('nonconformities/dashboard.html',
                         total_nc=total_nc,
                         open_nc=open_nc,
                         closed_nc=closed_nc,
                         critical_nc=critical_nc,
                         major_nc=major_nc,
                         minor_nc=minor_nc,
                         nc_by_origin=nc_by_origin,
                         nc_by_status=nc_by_status,
                         avg_resolution_time=avg_resolution_time,
                         recurrent_nc=recurrent_nc,
                         overdue_nc=overdue_nc,
                         nc_trend=nc_trend,
                         top_controls=top_controls)


@nonconformities_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """Crear nueva no conformidad"""

    if request.method == 'POST':
        try:
            # Crear la NC
            # Parsear fecha de detección (puede venir con hora o solo fecha)
            detection_date_str = request.form.get('detection_date')
            if 'T' in detection_date_str:
                detection_date = datetime.strptime(detection_date_str, '%Y-%m-%dT%H:%M')
            else:
                detection_date = datetime.strptime(detection_date_str, '%Y-%m-%d')

            # Parsear fecha objetivo de cierre
            target_closure_date = None
            target_closure_date_str = request.form.get('target_closure_date')
            if target_closure_date_str:
                target_closure_date = datetime.strptime(target_closure_date_str, '%Y-%m-%d').date()

            nc = NonConformity(
                nc_number=NonConformity.generate_nc_number(),
                title=request.form.get('title'),
                description=request.form.get('description'),
                origin=NCOrigin[request.form.get('origin')],
                severity=NCSeverity[request.form.get('severity')],
                status=NCStatus.NEW,
                detection_date=detection_date,
                reported_date=datetime.utcnow(),
                reported_by_id=current_user.id,
                responsible_id=int(request.form.get('responsible_id')),
                target_closure_date=target_closure_date,
                immediate_action=request.form.get('immediate_action'),
                notes=request.form.get('notes'),
                created_by_id=current_user.id
            )

            # Controles afectados (múltiples selección)
            affected_controls = request.form.getlist('affected_controls')
            if affected_controls:
                nc.affected_controls = affected_controls

            # Si viene de auditoría
            if request.form.get('audit_id'):
                nc.audit_id = int(request.form.get('audit_id'))

            # Si viene de incidente
            if request.form.get('incident_id'):
                nc.incident_id = int(request.form.get('incident_id'))

            # Si es recurrente
            if request.form.get('is_recurrent') == 'on':
                nc.is_recurrent = True
                if request.form.get('related_nc_id'):
                    nc.related_nc_id = int(request.form.get('related_nc_id'))

            db.session.add(nc)

            # Crear evento en timeline
            timeline_event = NCTimeline(
                nonconformity=nc,
                event_type=NCTimelineEventType.CREATED,
                description=f"No conformidad creada por {current_user.name}",
                user_id=current_user.id
            )
            db.session.add(timeline_event)

            # Activos afectados
            asset_ids = request.form.getlist('asset_ids')
            for asset_id in asset_ids:
                nc_asset = NCAsset(
                    nonconformity=nc,
                    asset_id=int(asset_id)
                )
                db.session.add(nc_asset)

            db.session.commit()

            flash(f'No conformidad {nc.nc_number} creada exitosamente', 'success')
            return redirect(url_for('nonconformities.view', id=nc.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la no conformidad: {str(e)}', 'danger')

    # GET - Mostrar formulario
    users = User.query.filter_by(is_active=True).all()
    audits = Audit.query.filter(Audit.status.in_(['in_progress', 'completed'])).all()
    assets = Asset.query.all()

    # Obtener controles SOA de la versión actual
    from models import SOAControl, SOAVersion
    current_version = SOAVersion.get_current_version()
    controls = []
    if current_version:
        controls = SOAControl.query.filter_by(
            soa_version_id=current_version.id
        ).order_by(SOAControl.control_id).all()

    return render_template('nonconformities/create.html',
                         users=users,
                         audits=audits,
                         assets=assets,
                         controls=controls,
                         NCOrigin=NCOrigin,
                         NCSeverity=NCSeverity)


@nonconformities_bp.route('/<int:id>')
@login_required
def view(id):
    """Ver detalle de una no conformidad"""
    nc = NonConformity.query.get_or_404(id)

    # Calcular métricas
    days_open = nc.calculate_days_open()
    resolution_time = nc.calculate_resolution_time()
    progress = nc.get_progress_percentage()
    is_overdue = nc.is_overdue()

    # Obtener lista de usuarios activos para formularios
    users = User.query.filter_by(is_active=True).all()

    return render_template('nonconformities/detail.html',
                         nc=nc,
                         days_open=days_open,
                         resolution_time=resolution_time,
                         progress=progress,
                         is_overdue=is_overdue,
                         users=users,
                         NCStatus=NCStatus,
                         ActionStatus=ActionStatus)


@nonconformities_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Editar no conformidad"""
    nc = NonConformity.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Parsear fecha objetivo de cierre
            target_closure_date = None
            target_closure_date_str = request.form.get('target_closure_date')
            if target_closure_date_str:
                target_closure_date = datetime.strptime(target_closure_date_str, '%Y-%m-%d').date()

            # Actualizar campos
            nc.title = request.form.get('title')
            nc.description = request.form.get('description')
            nc.severity = NCSeverity[request.form.get('severity')]
            nc.responsible_id = int(request.form.get('responsible_id'))
            nc.target_closure_date = target_closure_date
            nc.notes = request.form.get('notes')
            nc.updated_by_id = current_user.id

            # Controles afectados
            affected_controls = request.form.getlist('affected_controls')
            if affected_controls:
                nc.affected_controls = affected_controls

            # Activos afectados - eliminar los anteriores y agregar los nuevos
            asset_ids = request.form.getlist('asset_ids')
            # Eliminar activos anteriores
            for nc_asset in nc.affected_assets:
                db.session.delete(nc_asset)
            # Agregar nuevos activos
            for asset_id in asset_ids:
                if asset_id:
                    nc_asset = NCAsset(
                        nonconformity_id=nc.id,
                        asset_id=int(asset_id)
                    )
                    db.session.add(nc_asset)

            # Crear evento en timeline
            timeline_event = NCTimeline(
                nonconformity=nc,
                event_type=NCTimelineEventType.COMMENT,
                description=f"No conformidad actualizada por {current_user.name}",
                user_id=current_user.id
            )
            db.session.add(timeline_event)

            db.session.commit()
            flash('No conformidad actualizada exitosamente', 'success')
            return redirect(url_for('nonconformities.view', id=nc.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')

    # GET
    users = User.query.filter_by(is_active=True).all()
    assets = Asset.query.all()

    # Obtener controles SOA de la versión actual
    from models import SOAControl, SOAVersion
    current_version = SOAVersion.get_current_version()
    controls = []
    if current_version:
        controls = SOAControl.query.filter_by(
            soa_version_id=current_version.id
        ).order_by(SOAControl.control_id).all()

    return render_template('nonconformities/edit.html',
                         nc=nc,
                         users=users,
                         assets=assets,
                         controls=controls,
                         NCSeverity=NCSeverity)


@nonconformities_bp.route('/<int:id>/change-status', methods=['POST'])
@login_required
def change_status(id):
    """Cambiar estado de la NC"""
    nc = NonConformity.query.get_or_404(id)

    try:
        old_status = nc.status
        new_status = NCStatus[request.form.get('new_status')]

        nc.status = new_status
        nc.updated_by_id = current_user.id

        # Actualizar fechas según estado
        if new_status == NCStatus.ANALYZING:
            nc.analysis_start_date = datetime.utcnow()
        elif new_status == NCStatus.ACTION_PLAN:
            nc.action_plan_date = datetime.utcnow()
        elif new_status == NCStatus.IMPLEMENTING:
            nc.implementation_start_date = datetime.utcnow()
        elif new_status == NCStatus.VERIFYING:
            nc.verification_date = datetime.utcnow()
        elif new_status == NCStatus.CLOSED:
            nc.closure_date = datetime.utcnow()

        # Crear evento en timeline
        timeline_event = NCTimeline(
            nonconformity=nc,
            event_type=NCTimelineEventType.STATUS_CHANGE,
            description=f"Estado cambiado de {old_status.value} a {new_status.value}",
            user_id=current_user.id,
            old_value=old_status.value,
            new_value=new_status.value
        )
        db.session.add(timeline_event)

        db.session.commit()
        flash(f'Estado cambiado a {new_status.value}', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar estado: {str(e)}', 'danger')

    return redirect(url_for('nonconformities.view', id=id))


@nonconformities_bp.route('/<int:id>/rca', methods=['POST'])
@login_required
def add_rca(id):
    """Añadir análisis de causa raíz (RCA) - ISO 27001:2023 - 10.2.b"""
    nc = NonConformity.query.get_or_404(id)

    try:
        nc.rca_method = RCAMethod[request.form.get('rca_method')]
        nc.root_cause_analysis = request.form.get('root_cause_analysis')

        # Causas raíz (JSON array)
        root_causes = request.form.get('root_causes', '').split('\n')
        nc.root_causes = [cause.strip() for cause in root_causes if cause.strip()]

        # Factores contribuyentes
        contributing_factors = request.form.get('contributing_factors', '').split('\n')
        nc.contributing_factors = [factor.strip() for factor in contributing_factors if factor.strip()]

        # Análisis de NC similares (10.2.b.3)
        nc.similar_nc_analysis = request.form.get('similar_nc_analysis')

        nc.updated_by_id = current_user.id

        # Si estaba en estado NEW, cambiar a ANALYZING
        if nc.status == NCStatus.NEW:
            nc.status = NCStatus.ANALYZING
            nc.analysis_start_date = datetime.utcnow()

        # Timeline event
        timeline_event = NCTimeline(
            nonconformity=nc,
            event_type=NCTimelineEventType.RCA_COMPLETED,
            description=f"Análisis de causa raíz completado usando método: {nc.rca_method.value}",
            user_id=current_user.id,
            details={'method': nc.rca_method.value, 'root_causes': nc.root_causes}
        )
        db.session.add(timeline_event)

        db.session.commit()
        flash('Análisis de causa raíz añadido exitosamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al añadir RCA: {str(e)}', 'danger')

    return redirect(url_for('nonconformities.view', id=id))


@nonconformities_bp.route('/<int:id>/actions/new', methods=['POST'])
@login_required
def add_action(id):
    """Añadir acción correctiva/preventiva - ISO 27001:2023 - 10.2.c"""
    nc = NonConformity.query.get_or_404(id)

    try:
        action = CorrectiveAction(
            nonconformity_id=nc.id,
            action_type=ActionType[request.form.get('action_type')],
            description=request.form.get('description'),
            implementation_plan=request.form.get('implementation_plan'),
            resources_required=request.form.get('resources_required'),
            responsible_id=int(request.form.get('responsible_id')),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date(),
            verification_method=request.form.get('verification_method'),
            verification_criteria=request.form.get('verification_criteria'),
            priority=int(request.form.get('priority', 3)),
            notes=request.form.get('notes')
        )

        db.session.add(action)

        # Timeline event
        timeline_event = NCTimeline(
            nonconformity=nc,
            event_type=NCTimelineEventType.ACTION_ADDED,
            description=f"Acción {action.action_type.value} añadida: {action.description[:50]}...",
            user_id=current_user.id
        )
        db.session.add(timeline_event)

        # Cambiar estado si es necesario
        if nc.status == NCStatus.ANALYZING:
            nc.status = NCStatus.ACTION_PLAN
            nc.action_plan_date = datetime.utcnow()

        db.session.commit()
        flash('Acción añadida exitosamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al añadir acción: {str(e)}', 'danger')

    return redirect(url_for('nonconformities.view', id=id))


@nonconformities_bp.route('/actions/<int:action_id>/complete', methods=['POST'])
@login_required
def complete_action(action_id):
    """Marcar acción como completada"""
    action = CorrectiveAction.query.get_or_404(action_id)

    try:
        action.status = ActionStatus.COMPLETED
        action.completion_date = datetime.now().date()
        action.evidence_description = request.form.get('evidence_description')

        # Timeline event
        timeline_event = NCTimeline(
            nonconformity_id=action.nonconformity_id,
            event_type=NCTimelineEventType.ACTION_COMPLETED,
            description=f"Acción completada: {action.description[:50]}...",
            user_id=current_user.id
        )
        db.session.add(timeline_event)

        # Cambiar estado de NC si es necesario
        if action.nonconformity.status == NCStatus.ACTION_PLAN:
            action.nonconformity.status = NCStatus.IMPLEMENTING
            action.nonconformity.implementation_start_date = datetime.utcnow()

        db.session.commit()
        flash('Acción marcada como completada', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('nonconformities.view', id=action.nonconformity_id))


@nonconformities_bp.route('/<int:id>/verify', methods=['POST'])
@login_required
def verify_effectiveness(id):
    """Verificar eficacia de acciones correctivas - ISO 27001:2023 - 10.2.d"""
    nc = NonConformity.query.get_or_404(id)

    try:
        nc.effectiveness_verification = request.form.get('effectiveness_verification')
        nc.effectiveness_criteria = request.form.get('effectiveness_criteria')
        nc.is_effective = request.form.get('is_effective') == 'yes'
        nc.lessons_learned = request.form.get('lessons_learned')
        nc.verifier_id = current_user.id
        nc.verification_date = datetime.utcnow()

        # SGSI changes (10.2.e)
        nc.sgsi_changes_required = request.form.get('sgsi_changes_required') == 'yes'
        if nc.sgsi_changes_required:
            nc.sgsi_changes_description = request.form.get('sgsi_changes_description')

        # Timeline event
        timeline_event = NCTimeline(
            nonconformity=nc,
            event_type=NCTimelineEventType.VERIFICATION_COMPLETED,
            description=f"Verificación de eficacia completada. Resultado: {'Eficaz' if nc.is_effective else 'No eficaz'}",
            user_id=current_user.id
        )
        db.session.add(timeline_event)

        # Si es eficaz, puede cerrarse
        if nc.is_effective:
            nc.status = NCStatus.VERIFYING
        else:
            # Si no es eficaz, volver a plan de acción
            nc.status = NCStatus.ACTION_PLAN
            flash('Las acciones no fueron eficaces. Se requiere un nuevo plan de acción.', 'warning')

        db.session.commit()
        flash('Verificación de eficacia registrada', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('nonconformities.view', id=id))


@nonconformities_bp.route('/<int:id>/close', methods=['POST'])
@login_required
def close_nc(id):
    """Cerrar definitivamente la NC"""
    nc = NonConformity.query.get_or_404(id)

    try:
        # Validar que esté verificada
        if not nc.is_effective:
            flash('No se puede cerrar una NC sin verificación eficaz', 'warning')
            return redirect(url_for('nonconformities.view', id=id))

        # Validar que todas las acciones estén completadas
        pending_actions = [a for a in nc.actions if a.status != ActionStatus.COMPLETED and a.status != ActionStatus.VERIFIED]
        if pending_actions:
            flash(f'Hay {len(pending_actions)} acciones pendientes. Complete todas las acciones antes de cerrar.', 'warning')
            return redirect(url_for('nonconformities.view', id=id))

        nc.status = NCStatus.CLOSED
        nc.closure_date = datetime.utcnow()
        nc.updated_by_id = current_user.id

        # Timeline event
        timeline_event = NCTimeline(
            nonconformity=nc,
            event_type=NCTimelineEventType.CLOSURE,
            description=f"No conformidad cerrada por {current_user.name}",
            user_id=current_user.id
        )
        db.session.add(timeline_event)

        db.session.commit()
        flash(f'No conformidad {nc.nc_number} cerrada exitosamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('nonconformities.view', id=id))


@nonconformities_bp.route('/<int:id>/reopen', methods=['POST'])
@login_required
def reopen_nc(id):
    """Reabrir una NC cerrada"""
    nc = NonConformity.query.get_or_404(id)

    try:
        reason = request.form.get('reason', '')

        nc.status = NCStatus.REOPENED
        nc.updated_by_id = current_user.id

        # Timeline event
        timeline_event = NCTimeline(
            nonconformity=nc,
            event_type=NCTimelineEventType.REOPENED,
            description=f"No conformidad reabierta por {current_user.name}. Razón: {reason}",
            user_id=current_user.id
        )
        db.session.add(timeline_event)

        db.session.commit()
        flash('No conformidad reabierta', 'warning')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('nonconformities.view', id=id))


@nonconformities_bp.route('/<int:id>/upload', methods=['POST'])
@login_required
def upload_attachment(id):
    """Subir archivo adjunto"""
    nc = NonConformity.query.get_or_404(id)

    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'warning')
        return redirect(url_for('nonconformities.view', id=id))

    file = request.files['file']

    if file.filename == '':
        flash('No se seleccionó ningún archivo', 'warning')
        return redirect(url_for('nonconformities.view', id=id))

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"

            # Crear directorio si no existe
            upload_path = os.path.join(UPLOAD_FOLDER, str(nc.id))
            os.makedirs(upload_path, exist_ok=True)

            file_path = os.path.join(upload_path, filename)
            file.save(file_path)

            # Crear registro de adjunto
            attachment = NCAttachment(
                nonconformity=nc,
                file_name=file.filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                file_type=file.content_type,
                description=request.form.get('description', ''),
                attachment_type=request.form.get('attachment_type', 'other'),
                uploaded_by_id=current_user.id
            )
            db.session.add(attachment)

            # Timeline event
            timeline_event = NCTimeline(
                nonconformity=nc,
                event_type=NCTimelineEventType.ATTACHMENT_ADDED,
                description=f"Archivo adjunto: {file.filename}",
                user_id=current_user.id
            )
            db.session.add(timeline_event)

            db.session.commit()
            flash('Archivo subido exitosamente', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al subir archivo: {str(e)}', 'danger')
    else:
        flash('Tipo de archivo no permitido', 'warning')

    return redirect(url_for('nonconformities.view', id=id))


@nonconformities_bp.route('/attachments/<int:attachment_id>/download')
@login_required
def download_attachment(attachment_id):
    """Descargar archivo adjunto"""
    attachment = NCAttachment.query.get_or_404(attachment_id)

    try:
        from flask import send_file
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.file_name
        )
    except Exception as e:
        flash(f'Error al descargar archivo: {str(e)}', 'danger')
        return redirect(url_for('nonconformities.view', id=attachment.nonconformity_id))


@nonconformities_bp.route('/attachments/<int:attachment_id>/delete', methods=['POST'])
@login_required
def delete_attachment(attachment_id):
    """Eliminar archivo adjunto"""
    attachment = NCAttachment.query.get_or_404(attachment_id)
    nc_id = attachment.nonconformity_id

    try:
        # Eliminar archivo físico
        if os.path.exists(attachment.file_path):
            os.remove(attachment.file_path)

        # Eliminar registro de base de datos
        db.session.delete(attachment)

        # Timeline event
        timeline_event = NCTimeline(
            nonconformity_id=nc_id,
            event_type=NCTimelineEventType.COMMENT,
            description=f"Archivo eliminado: {attachment.file_name}",
            user_id=current_user.id
        )
        db.session.add(timeline_event)

        db.session.commit()
        flash('Archivo eliminado exitosamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar archivo: {str(e)}', 'danger')

    return redirect(url_for('nonconformities.view', id=nc_id))


@nonconformities_bp.route('/metrics')
@login_required
def metrics():
    """Página de métricas e indicadores detallados"""
    # Este endpoint renderizará un dashboard completo con gráficos
    # Reutilizará datos del dashboard() pero con más detalle
    return dashboard()


@nonconformities_bp.route('/api/data')
@login_required
def api_data():
    """API para obtener datos en formato JSON (para gráficos)"""

    data_type = request.args.get('type', 'overview')

    if data_type == 'overview':
        return jsonify({
            'total': NonConformity.query.count(),
            'open': NonConformity.query.filter(NonConformity.status != NCStatus.CLOSED).count(),
            'closed': NonConformity.query.filter(NonConformity.status == NCStatus.CLOSED).count(),
            'critical': NonConformity.query.filter(NonConformity.severity == NCSeverity.CRITICAL).count()
        })

    elif data_type == 'by_status':
        nc_by_status = db.session.query(
            NonConformity.status,
            func.count(NonConformity.id)
        ).group_by(NonConformity.status).all()

        return jsonify({
            'labels': [status.value for status, _ in nc_by_status],
            'data': [count for _, count in nc_by_status]
        })

    elif data_type == 'trend':
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        nc_trend = db.session.query(
            extract('year', NonConformity.reported_date).label('year'),
            extract('month', NonConformity.reported_date).label('month'),
            func.count(NonConformity.id).label('count')
        ).filter(
            NonConformity.reported_date >= six_months_ago
        ).group_by('year', 'month').order_by('year', 'month').all()

        return jsonify({
            'labels': [f"{int(year)}-{int(month):02d}" for year, month, _ in nc_trend],
            'data': [count for _, _, count in nc_trend]
        })

    return jsonify({'error': 'Invalid data type'}), 400
