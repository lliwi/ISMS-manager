from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import (Risk, Incident, NonConformity, SOAControl, Audit, SOAVersion,
                    Document, Asset, Service, TrainingSession)
from models import IncidentStatus, NCStatus
from app.models.task import Task, PeriodicTaskStatus
from app.models.change import Change, ChangeStatus
from app.models.audit import (AuditProgram, AuditFinding as Finding,
                              AuditCorrectiveAction as CorrectiveAction,
                              FindingStatus, AuditActionStatus)
from app.risks.models import Riesgo
from datetime import datetime, timedelta, date
from sqlalchemy import func, and_, or_, case, extract
from collections import defaultdict

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Calculate KPIs and metrics for the dashboard
    kpis = {}

    # SOA Controls metrics
    total_controls = SOAControl.query.count()
    implemented_controls = SOAControl.query.filter_by(implementation_status='implemented').count()
    kpis['soa_compliance'] = (implemented_controls / total_controls * 100) if total_controls > 0 else 0

    # Risk metrics - usando tabla riesgos (sistema avanzado)
    total_risks = Riesgo.query.count()
    # Contar riesgos ALTO y MUY_ALTO
    high_risks = Riesgo.query.filter(
        Riesgo.clasificacion_efectiva.in_(['ALTO', 'MUY_ALTO'])
    ).count()
    kpis['high_risk_count'] = high_risks
    kpis['total_risks'] = total_risks

    # Incident metrics
    open_incidents = Incident.query.filter(~Incident.status.in_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED])).count()
    total_incidents_month = Incident.query.filter(
        Incident.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    kpis['open_incidents'] = open_incidents
    kpis['incidents_this_month'] = total_incidents_month

    # Non-conformities metrics
    open_nonconformities = NonConformity.query.filter(
        ~NonConformity.status.in_([NCStatus.CLOSED])
    ).count()
    overdue_nonconformities = NonConformity.query.filter(
        NonConformity.target_closure_date < datetime.utcnow().date(),
        NonConformity.status != NCStatus.CLOSED
    ).count()
    kpis['open_nonconformities'] = open_nonconformities
    kpis['overdue_nonconformities'] = overdue_nonconformities

    # Tasks metrics
    overdue_tasks = Task.query.filter(
        Task.due_date < datetime.utcnow(),
        Task.status == PeriodicTaskStatus.VENCIDA
    ).count()
    pending_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_([PeriodicTaskStatus.PENDIENTE, PeriodicTaskStatus.EN_PROGRESO])
    ).count()
    kpis['overdue_tasks'] = overdue_tasks
    kpis['my_pending_tasks'] = pending_tasks

    # Document metrics
    approved_documents = Document.query.filter_by(status='approved').count()
    pending_review_documents = Document.query.filter_by(status='review').count()
    kpis['approved_documents'] = approved_documents
    kpis['pending_review_documents'] = pending_review_documents

    # Change metrics
    pending_changes = Change.query.filter(
        Change.status.in_([
            ChangeStatus.SUBMITTED,
            ChangeStatus.UNDER_REVIEW,
            ChangeStatus.PENDING_APPROVAL,
            ChangeStatus.APPROVED,
            ChangeStatus.SCHEDULED,
            ChangeStatus.IN_PROGRESS
        ])
    ).count()

    # Cambios aprobados/implementados este mes (usando updated_at como referencia)
    first_day_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    approved_changes_month = Change.query.filter(
        Change.status.in_([ChangeStatus.APPROVED, ChangeStatus.IMPLEMENTED, ChangeStatus.CLOSED]),
        Change.updated_at >= first_day_month
    ).count()

    kpis['pending_changes'] = pending_changes
    kpis['approved_changes_month'] = approved_changes_month

    # Recent activity
    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(5).all()
    recent_nonconformities = NonConformity.query.order_by(NonConformity.created_at.desc()).limit(5).all()
    my_tasks = Task.query.filter(
        Task.assigned_to_id == current_user.id,
        Task.status.in_([PeriodicTaskStatus.PENDIENTE, PeriodicTaskStatus.EN_PROGRESO])
    ).order_by(Task.due_date).limit(5).all()

    return render_template('dashboard/index.html',
                         kpis=kpis,
                         recent_incidents=recent_incidents,
                         recent_nonconformities=recent_nonconformities,
                         my_tasks=my_tasks,
                         current_datetime=datetime.utcnow())


@dashboard_bp.route('/api/soa-radar-data')
@login_required
def soa_radar_data():
    """
    API endpoint para obtener datos del gráfico de radar de SOA
    Agrupa controles por categoría y calcula madurez promedio
    """
    try:
        # Obtener la versión actual del SOA
        current_soa = SOAVersion.get_current_version()

        if not current_soa:
            # Si no hay versión activa, obtener todos los controles sin filtrar por versión
            controls = SOAControl.query.filter_by(
                applicability_status='aplicable'
            ).all()

            if not controls:
                return jsonify({'error': 'No hay controles SOA en el sistema. Por favor, inicializa el SOA primero.'}), 404

            soa_version_name = 'Sin versión definida'
        else:
            # Obtener controles aplicables de la versión actual
            controls = SOAControl.query.filter_by(
                soa_version_id=current_soa.id,
                applicability_status='aplicable'
            ).all()

            if not controls:
                return jsonify({'error': 'No hay controles aplicables en la versión actual del SOA'}), 404

            soa_version_name = f"{current_soa.title} (v{current_soa.version_number})"

        # Agrupar controles por categoría y calcular madurez promedio
        category_data = defaultdict(lambda: {'total': 0, 'maturity_sum': 0, 'controls': []})

        for control in controls:
            category = control.category
            maturity_score = control.maturity_score  # Es una propiedad, no un método

            category_data[category]['total'] += 1
            category_data[category]['maturity_sum'] += maturity_score
            category_data[category]['controls'].append({
                'control_id': control.control_id,
                'title': control.title,
                'maturity_level': control.maturity_level,
                'maturity_score': maturity_score
            })

        # Calcular promedio de madurez por categoría
        categories = []
        maturity_scores = []
        control_counts = []

        for category, data in sorted(category_data.items()):
            avg_maturity = (data['maturity_sum'] / data['total']) if data['total'] > 0 else 0

            categories.append(category)
            maturity_scores.append(round(avg_maturity, 2))
            control_counts.append(data['total'])

        # Preparar respuesta
        response = {
            'categories': categories,
            'maturity_scores': maturity_scores,
            'control_counts': control_counts,
            'total_controls': len(controls),
            'soa_version': soa_version_name,
            'max_maturity': 6,  # Escala 0-6 (no_implementado a optimizado)
            'maturity_labels': {
                0: 'No Implementado',
                1: 'Inicial',
                2: 'Repetible',
                3: 'Definido',
                4: 'Controlado',
                5: 'Cuantificado',
                6: 'Optimizado'
            }
        }

        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@dashboard_bp.route('/api/soa-applicability-map')
@login_required
def soa_applicability_map():
    """API endpoint para el mapa de aplicabilidad del SOA"""
    try:
        # Obtener la versión actual del SOA
        current_soa = SOAVersion.get_current_version()

        if not current_soa:
            return jsonify({'error': 'No hay versión activa del SOA'})

        # Obtener todos los controles ordenados por control_id
        controls = SOAControl.query.filter_by(
            soa_version_id=current_soa.id
        ).order_by(SOAControl.control_id).all()

        # Serializar controles
        controls_data = []
        for control in controls:
            controls_data.append({
                'control_id': control.control_id,
                'title': control.title,
                'category': control.category or 'Sin categoría',
                'applicability_status': control.applicability_status
            })

        return jsonify({
            'soa_version': f"{current_soa.title} (v{current_soa.version_number})",
            'controls': controls_data
        })

    except Exception as e:
        print(f"Error en soa_applicability_map: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al cargar datos: {str(e)}'})


@dashboard_bp.route('/api/soa-controls-radar-data')
@login_required
def soa_controls_radar_data():
    """
    API endpoint para obtener datos del gráfico de radar de controles SOA
    Muestra controles individuales agrupados por dominio ISO 27001
    """
    try:
        # Obtener la versión actual del SOA
        current_soa = SOAVersion.get_current_version()

        if not current_soa:
            # Si no hay versión activa, obtener todos los controles sin filtrar por versión
            controls = SOAControl.query.filter_by(
                applicability_status='aplicable'
            ).all()
            soa_version_name = 'Sin versión definida'
        else:
            # Obtener controles aplicables de la versión actual
            controls = SOAControl.query.filter_by(
                soa_version_id=current_soa.id,
                applicability_status='aplicable'
            ).all()
            soa_version_name = f"{current_soa.title} (v{current_soa.version_number})"

        if not controls:
            return jsonify({'error': 'No hay controles aplicables en el sistema'}), 404

        # Agrupar controles por dominio (A.5, A.6, A.7, A.8)
        domain_data = defaultdict(lambda: {'controls': [], 'maturity_sum': 0, 'total': 0})

        for control in controls:
            # Extraer dominio del control_id (ej: A.5.1 -> A.5)
            domain = control.control_id[:3] if len(control.control_id) >= 3 else 'Otro'
            maturity_score = control.maturity_score

            domain_data[domain]['controls'].append({
                'control_id': control.control_id,
                'title': control.title,
                'maturity_score': maturity_score,
                'category': control.category
            })
            domain_data[domain]['maturity_sum'] += maturity_score
            domain_data[domain]['total'] += 1

        # Seleccionar los controles más representativos de cada dominio
        # (los de mayor impacto o más críticos)
        selected_controls = []
        control_labels = []
        maturity_scores = []
        control_details = []

        # Límite de controles a mostrar (evitar saturación del gráfico)
        max_controls_per_domain = 5

        # Nombres de dominios ISO 27001:2022
        domain_names = {
            'A.5': 'Organizacional',
            'A.6': 'Personas',
            'A.7': 'Físico',
            'A.8': 'Tecnológico'
        }

        for domain in sorted(domain_data.keys()):
            domain_controls = domain_data[domain]['controls']

            # Ordenar por madurez (mostrar controles con diferentes niveles)
            # Mezclamos altos y bajos para mejor visualización
            sorted_controls = sorted(domain_controls, key=lambda x: x['maturity_score'], reverse=True)

            # Tomar hasta max_controls_per_domain controles representativos
            for i, control in enumerate(sorted_controls[:max_controls_per_domain]):
                # Crear etiqueta corta para el gráfico
                short_label = f"{control['control_id']}"
                full_label = f"{control['control_id']} - {control['title'][:30]}..."

                control_labels.append(short_label)
                maturity_scores.append(control['maturity_score'])
                control_details.append({
                    'control_id': control['control_id'],
                    'title': control['title'],
                    'domain': domain_names.get(domain, domain),
                    'category': control['category'],
                    'maturity_score': control['maturity_score'],
                    'full_label': full_label
                })

        # Preparar respuesta
        response = {
            'control_labels': control_labels,
            'maturity_scores': maturity_scores,
            'control_details': control_details,
            'total_controls_shown': len(control_labels),
            'total_controls': len(controls),
            'soa_version': soa_version_name,
            'max_maturity': 6,
            'domains': {
                domain: {
                    'name': domain_names.get(domain, domain),
                    'total': data['total'],
                    'avg_maturity': round(data['maturity_sum'] / data['total'], 2) if data['total'] > 0 else 0
                }
                for domain, data in domain_data.items()
            }
        }

        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


# ============================================================================
# NUEVOS ENDPOINTS - FASE 1: ALERTAS CRÍTICAS Y MÉTRICAS OPERATIVAS
# ============================================================================

@dashboard_bp.route('/api/critical-alerts')
@login_required
def critical_alerts():
    """
    API endpoint para obtener todas las alertas críticas consolidadas
    """
    try:
        alerts = []
        today = date.today()

        # 1. Riesgos críticos (nivel 9-10)
        critical_risks = Riesgo.query.filter(
            Riesgo.nivel_riesgo_efectivo >= 9
        ).all()

        for risk in critical_risks:
            # Construir nombre descriptivo del riesgo
            risk_name = risk.codigo
            if risk.activo and hasattr(risk.activo, 'nombre'):
                risk_name = f"{risk.codigo} - {risk.activo.nombre}"
            elif risk.amenaza and hasattr(risk.amenaza, 'nombre'):
                risk_name = f"{risk.codigo} - {risk.amenaza.nombre}"

            alerts.append({
                'type': 'risk',
                'severity': 'critical',
                'title': f'Riesgo Crítico: {risk_name}',
                'description': f'Nivel de riesgo: {float(risk.nivel_riesgo_efectivo) if risk.nivel_riesgo_efectivo else 0}',
                'url': f'/riesgos/{risk.id}',
                'date': risk.created_at.date().isoformat() if risk.created_at else None
            })

        # 2. Incidentes críticos abiertos
        critical_incidents = Incident.query.filter(
            Incident.severity.in_(['CRITICAL', 'HIGH']),
            ~Incident.status.in_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED])
        ).all()

        for incident in critical_incidents:
            alerts.append({
                'type': 'incident',
                'severity': 'critical' if incident.severity == 'CRITICAL' else 'high',
                'title': f'Incidente: {incident.title}',
                'description': f'Estado: {incident.status.value}',
                'url': f'/incidentes/{incident.id}',
                'date': incident.created_at.date().isoformat()
            })

        # 3. Tareas vencidas
        overdue_tasks = Task.query.filter(
            Task.due_date < datetime.utcnow(),
            Task.status == PeriodicTaskStatus.VENCIDA
        ).all()

        for task in overdue_tasks:
            days_overdue = (today - task.due_date.date()).days
            alerts.append({
                'type': 'task',
                'severity': 'high' if days_overdue > 7 else 'medium',
                'title': f'Tarea Vencida: {task.title}',
                'description': f'Vencida hace {days_overdue} días',
                'url': f'/tareas/{task.id}',
                'date': task.due_date.date().isoformat()
            })

        # 4. Documentos vencidos para revisión
        overdue_docs = Document.query.filter(
            Document.next_review_date.isnot(None),
            Document.next_review_date < today,
            Document.status.in_(['approved', 'review'])
        ).all()

        for doc in overdue_docs:
            days_overdue = (today - doc.next_review_date).days
            alerts.append({
                'type': 'document',
                'severity': 'medium',
                'title': f'Documento Vencido: {doc.title}',
                'description': f'Revisión vencida hace {days_overdue} días',
                'url': f'/documentos/{doc.id}',
                'date': doc.next_review_date.isoformat()
            })

        # 5. Activos con garantía por vencer (próximos 30 días)
        warranty_expiring = Asset.query.filter(
            Asset.warranty_expiry.isnot(None),
            Asset.warranty_expiry >= today,
            Asset.warranty_expiry <= today + timedelta(days=30)
        ).all()

        for asset in warranty_expiring:
            days_left = (asset.warranty_expiry - today).days
            alerts.append({
                'type': 'asset',
                'severity': 'low' if days_left > 15 else 'medium',
                'title': f'Garantía por Vencer: {asset.name}',
                'description': f'Vence en {days_left} días',
                'url': f'/activos/{asset.id}',
                'date': asset.warranty_expiry.isoformat()
            })

        # 6. Acciones correctivas vencidas
        overdue_actions = CorrectiveAction.query.filter(
            CorrectiveAction.planned_completion_date < today,
            CorrectiveAction.status.in_([AuditActionStatus.PENDING, AuditActionStatus.IN_PROGRESS])
        ).all()

        for action in overdue_actions:
            days_overdue = (today - action.planned_completion_date).days
            alerts.append({
                'type': 'corrective_action',
                'severity': 'high',
                'title': f'Acción Correctiva Vencida: {action.description[:50]}',
                'description': f'Vencida hace {days_overdue} días',
                'url': f'/auditorias/acciones-correctivas/{action.id}',
                'date': action.planned_completion_date.isoformat()
            })

        # Ordenar por severidad y fecha
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        alerts.sort(key=lambda x: (severity_order.get(x['severity'], 99), x['date'] or ''))

        return jsonify({
            'alerts': alerts,
            'total': len(alerts),
            'by_severity': {
                'critical': len([a for a in alerts if a['severity'] == 'critical']),
                'high': len([a for a in alerts if a['severity'] == 'high']),
                'medium': len([a for a in alerts if a['severity'] == 'medium']),
                'low': len([a for a in alerts if a['severity'] == 'low'])
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener alertas: {str(e)}'}), 500


@dashboard_bp.route('/api/operational-metrics')
@login_required
def operational_metrics():
    """
    API endpoint para métricas operativas clave
    """
    try:
        metrics = {}

        # 1. Tasa de completitud de tareas (%)
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter(
            Task.status == PeriodicTaskStatus.COMPLETADA
        ).count()
        metrics['task_completion_rate'] = round(
            (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2
        )

        # 2. Tasa de efectividad de NC (%)
        total_nc_closed = NonConformity.query.filter(
            NonConformity.status == NCStatus.CLOSED
        ).count()
        effective_nc = total_nc_closed
        total_nc = NonConformity.query.count()
        metrics['nc_effectiveness_rate'] = round(
            (effective_nc / total_nc * 100) if total_nc > 0 else 0, 2
        )

        # 3. Tiempo promedio de respuesta a incidentes (en días)
        resolved_incidents = Incident.query.filter(
            Incident.status.in_([IncidentStatus.RESOLVED, IncidentStatus.CLOSED]),
            Incident.resolution_date.isnot(None)
        ).all()

        if resolved_incidents:
            total_response_time = sum([
                (inc.resolution_date - inc.discovery_date).days
                for inc in resolved_incidents
                if inc.discovery_date
            ])
            metrics['avg_incident_response_days'] = round(
                total_response_time / len(resolved_incidents), 2
            )
        else:
            metrics['avg_incident_response_days'] = 0

        # 4. Tasa de éxito de cambios (%)
        total_changes = Change.query.filter(
            Change.status.in_([
                ChangeStatus.IMPLEMENTED,
                ChangeStatus.CLOSED,
                ChangeStatus.FAILED,
                ChangeStatus.ROLLED_BACK
            ])
        ).count()

        successful_changes = Change.query.filter(
            Change.status.in_([ChangeStatus.IMPLEMENTED, ChangeStatus.CLOSED])
        ).count()

        metrics['change_success_rate'] = round(
            (successful_changes / total_changes * 100) if total_changes > 0 else 0, 2
        )

        return jsonify(metrics)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener métricas operativas: {str(e)}'}), 500


# ============================================================================
# FASE 2: RIESGOS Y AUDITORÍAS
# ============================================================================

@dashboard_bp.route('/api/risk-heatmap')
@login_required
def risk_heatmap():
    """
    API endpoint para mapa de calor de riesgos (impacto vs probabilidad)
    """
    try:
        risks = Riesgo.query.all()
        heatmap_data = []

        for risk in risks:
            # Construir nombre descriptivo del riesgo
            risk_name = risk.codigo
            if risk.activo and hasattr(risk.activo, 'nombre'):
                risk_name = f"{risk.codigo} - {risk.activo.nombre}"
            elif risk.amenaza and hasattr(risk.amenaza, 'nombre'):
                risk_name = f"{risk.codigo} - {risk.amenaza.nombre}"

            heatmap_data.append({
                'id': risk.id,
                'nombre': risk_name,
                'probabilidad': float(risk.probabilidad_efectiva) if risk.probabilidad_efectiva else 0,
                'impacto': float(risk.impacto_efectivo) if risk.impacto_efectivo else 0,
                'nivel': float(risk.nivel_riesgo_efectivo) if risk.nivel_riesgo_efectivo else 0,
                'clasificacion': risk.clasificacion_efectiva,
                'tratamiento': risk.tratamientos[0].opcion_tratamiento if risk.tratamientos else None
            })

        # Contar riesgos por celda de la matriz
        matrix = {}
        for i in range(1, 6):
            for j in range(1, 6):
                matrix[f"{i},{j}"] = {'count': 0, 'risks': []}

        for risk in heatmap_data:
            key = f"{risk['impacto']},{risk['probabilidad']}"
            if key in matrix:
                matrix[key]['count'] += 1
                matrix[key]['risks'].append({
                    'id': risk['id'],
                    'nombre': risk['nombre'],
                    'nivel': risk['nivel']
                })

        return jsonify({
            'risks': heatmap_data,
            'matrix': matrix,
            'total_risks': len(risks),
            'by_classification': {
                'MUY_ALTO': len([r for r in heatmap_data if r['clasificacion'] == 'MUY_ALTO']),
                'ALTO': len([r for r in heatmap_data if r['clasificacion'] == 'ALTO']),
                'MEDIO': len([r for r in heatmap_data if r['clasificacion'] == 'MEDIO']),
                'BAJO': len([r for r in heatmap_data if r['clasificacion'] == 'BAJO']),
                'MUY_BAJO': len([r for r in heatmap_data if r['clasificacion'] == 'MUY_BAJO'])
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al generar mapa de calor: {str(e)}'}), 500


@dashboard_bp.route('/api/audit-metrics')
@login_required
def audit_metrics():
    """
    API endpoint para métricas de auditoría
    """
    try:
        metrics = {}
        today = date.today()
        current_year = today.year

        # 1. Tasa de completitud de auditorías
        total_audits = Audit.query.filter(
            extract('year', Audit.start_date) == current_year
        ).count()

        completed_audits = Audit.query.filter(
            extract('year', Audit.start_date) == current_year,
            Audit.status.in_(['completed', 'closed'])
        ).count()

        metrics['audit_completion_rate'] = round(
            (completed_audits / total_audits * 100) if total_audits > 0 else 0, 2
        )

        # 2. Cobertura ISO 27001 (% controles implementados)
        total_iso_controls = SOAControl.query.filter_by(
            applicability_status='aplicable'
        ).count()

        implemented_controls = SOAControl.query.filter_by(
            applicability_status='aplicable',
            implementation_status='implemented'
        ).count()

        metrics['iso_coverage_percentage'] = round(
            (implemented_controls / total_iso_controls * 100) if total_iso_controls > 0 else 0, 2
        )

        # 3. Hallazgos abiertos
        open_findings = Finding.query.filter(
            Finding.status.in_([FindingStatus.OPEN, FindingStatus.ACTION_PLAN_PENDING,
                               FindingStatus.ACTION_PLAN_APPROVED, FindingStatus.IN_TREATMENT])
        ).count()
        metrics['open_findings'] = open_findings

        # 4. Acciones correctivas vencidas
        overdue_actions = CorrectiveAction.query.filter(
            CorrectiveAction.planned_completion_date < today,
            CorrectiveAction.status.in_([AuditActionStatus.PENDING, AuditActionStatus.IN_PROGRESS])
        ).count()
        metrics['overdue_corrective_actions'] = overdue_actions

        # 5. Hallazgos por nivel de riesgo
        metrics['findings_by_severity'] = {
            'critical': Finding.query.filter_by(risk_level='critical').count(),
            'high': Finding.query.filter_by(risk_level='high').count(),
            'medium': Finding.query.filter_by(risk_level='medium').count(),
            'low': Finding.query.filter_by(risk_level='low').count()
        }

        return jsonify(metrics)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener métricas de auditoría: {str(e)}'}), 500


# ============================================================================
# FASE 3: GRÁFICOS DE TENDENCIAS
# ============================================================================

@dashboard_bp.route('/api/trends/incidents')
@login_required
def trends_incidents():
    """
    API endpoint para tendencias de incidentes (últimos 6 meses)
    """
    try:
        today = datetime.utcnow()
        six_months_ago = today - timedelta(days=180)

        incidents_by_month = Incident.query.filter(
            Incident.created_at >= six_months_ago
        ).all()

        months = {}
        for i in range(6):
            month_date = today - timedelta(days=30*i)
            month_key = month_date.strftime('%Y-%m')
            month_name = month_date.strftime('%b %Y')
            months[month_key] = {'name': month_name, 'count': 0, 'critical': 0}

        for incident in incidents_by_month:
            month_key = incident.created_at.strftime('%Y-%m')
            if month_key in months:
                months[month_key]['count'] += 1
                if incident.severity in ['CRITICAL', 'HIGH']:
                    months[month_key]['critical'] += 1

        sorted_months = sorted(months.items(), key=lambda x: x[0])

        return jsonify({
            'labels': [m[1]['name'] for m in sorted_months],
            'data': [m[1]['count'] for m in sorted_months],
            'critical': [m[1]['critical'] for m in sorted_months]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener tendencias: {str(e)}'}), 500


@dashboard_bp.route('/api/trends/risks')
@login_required
def trends_risks():
    """
    API endpoint para evolución de riesgos en el tiempo
    """
    try:
        risks_by_level = {
            'MUY_ALTO': Riesgo.query.filter_by(clasificacion_efectiva='MUY_ALTO').count(),
            'ALTO': Riesgo.query.filter_by(clasificacion_efectiva='ALTO').count(),
            'MEDIO': Riesgo.query.filter_by(clasificacion_efectiva='MEDIO').count(),
            'BAJO': Riesgo.query.filter_by(clasificacion_efectiva='BAJO').count(),
            'MUY_BAJO': Riesgo.query.filter_by(clasificacion_efectiva='MUY_BAJO').count()
        }

        return jsonify({
            'labels': list(risks_by_level.keys()),
            'data': list(risks_by_level.values()),
            'total': sum(risks_by_level.values())
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener tendencias de riesgos: {str(e)}'}), 500


@dashboard_bp.route('/api/trends/tasks')
@login_required
def trends_tasks():
    """
    API endpoint para tendencias de tareas (últimos 6 meses)
    """
    try:
        today = datetime.utcnow()
        six_months_ago = today - timedelta(days=180)

        tasks = Task.query.filter(
            Task.created_at >= six_months_ago
        ).all()

        months = {}
        for i in range(6):
            month_date = today - timedelta(days=30*i)
            month_key = month_date.strftime('%Y-%m')
            month_name = month_date.strftime('%b %Y')
            months[month_key] = {
                'name': month_name,
                'created': 0,
                'completed': 0,
                'overdue': 0
            }

        for task in tasks:
            month_key = task.created_at.strftime('%Y-%m')
            if month_key in months:
                months[month_key]['created'] += 1
                if task.status == PeriodicTaskStatus.COMPLETADA:
                    months[month_key]['completed'] += 1
                elif task.status == PeriodicTaskStatus.VENCIDA:
                    months[month_key]['overdue'] += 1

        sorted_months = sorted(months.items(), key=lambda x: x[0])

        return jsonify({
            'labels': [m[1]['name'] for m in sorted_months],
            'created': [m[1]['created'] for m in sorted_months],
            'completed': [m[1]['completed'] for m in sorted_months],
            'overdue': [m[1]['overdue'] for m in sorted_months]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener tendencias de tareas: {str(e)}'}), 500


# ============================================================================
# FASE 4: ACTIVOS, SERVICIOS Y DOCUMENTOS
# ============================================================================

@dashboard_bp.route('/api/assets/distribution')
@login_required
def assets_distribution():
    """
    API endpoint para distribución de activos
    """
    try:
        assets_by_category = Asset.query.with_entities(
            Asset.category,
            func.count(Asset.id)
        ).group_by(Asset.category).all()

        assets_by_status = Asset.query.with_entities(
            Asset.status,
            func.count(Asset.id)
        ).group_by(Asset.status).all()

        critical_assets = Asset.query.filter(
            Asset.criticality >= 8
        ).count()

        return jsonify({
            'by_category': {
                cat.value if hasattr(cat, 'value') else str(cat): count
                for cat, count in assets_by_category if cat
            },
            'by_status': {
                status.value if hasattr(status, 'value') else str(status): count
                for status, count in assets_by_status if status
            },
            'critical_count': critical_assets,
            'total': Asset.query.count()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener distribución de activos: {str(e)}'}), 500


@dashboard_bp.route('/api/services/metrics')
@login_required
def services_metrics():
    """
    API endpoint para métricas de servicios
    """
    try:
        services_by_type = Service.query.with_entities(
            Service.service_type,
            func.count(Service.id)
        ).group_by(Service.service_type).all()

        services_by_status = Service.query.with_entities(
            Service.status,
            func.count(Service.id)
        ).group_by(Service.status).all()

        critical_services = Service.query.filter(
            Service.criticality >= 8
        ).count()

        services_with_rto = Service.query.filter(
            Service.rto.isnot(None)
        ).count()

        return jsonify({
            'by_type': {
                stype.value if hasattr(stype, 'value') else str(stype): count
                for stype, count in services_by_type if stype
            },
            'by_status': {
                status.value if hasattr(status, 'value') else str(status): count
                for status, count in services_by_status if status
            },
            'critical_count': critical_services,
            'with_rto_rpo': services_with_rto,
            'total': Service.query.count()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener métricas de servicios: {str(e)}'}), 500


@dashboard_bp.route('/api/documents/metrics')
@login_required
def documents_metrics():
    """
    API endpoint para métricas detalladas de documentos
    """
    try:
        today = date.today()

        overdue_docs = Document.query.filter(
            Document.next_review_date.isnot(None),
            Document.next_review_date < today,
            Document.status.in_(['approved', 'review'])
        ).count()

        docs_by_type = Document.query.with_entities(
            Document.document_type,
            func.count(Document.id)
        ).group_by(Document.document_type).all()

        docs_by_status = Document.query.with_entities(
            Document.status,
            func.count(Document.id)
        ).group_by(Document.status).all()

        return jsonify({
            'overdue_for_review': overdue_docs,
            'by_type': {
                dtype.value if hasattr(dtype, 'value') else str(dtype): count
                for dtype, count in docs_by_type if dtype
            },
            'by_status': {
                status: count for status, count in docs_by_status if status
            },
            'total': Document.query.count()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener métricas de documentos: {str(e)}'}), 500


# ============================================================================
# FASE 5: CAPACITACIÓN
# ============================================================================

@dashboard_bp.route('/api/training/metrics')
@login_required
def training_metrics():
    """
    API endpoint para métricas de capacitación
    """
    try:
        today = datetime.utcnow()

        upcoming_sessions = TrainingSession.query.filter(
            TrainingSession.date >= today,
            TrainingSession.date <= today + timedelta(days=30)
        ).count()

        current_year = today.year
        completed_sessions = TrainingSession.query.filter(
            extract('year', TrainingSession.date) == current_year,
            TrainingSession.status == 'COMPLETED'
        ).count()

        total_sessions_year = TrainingSession.query.filter(
            extract('year', TrainingSession.date) == current_year
        ).count()

        completion_rate = round(
            (completed_sessions / total_sessions_year * 100) if total_sessions_year > 0 else 0, 2
        )

        return jsonify({
            'upcoming_sessions': upcoming_sessions,
            'completed_this_year': completed_sessions,
            'total_this_year': total_sessions_year,
            'completion_rate': completion_rate
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener métricas de capacitación: {str(e)}'}), 500