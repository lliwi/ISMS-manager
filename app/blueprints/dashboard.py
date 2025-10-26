from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import Risk, Incident, NonConformity, SOAControl, Audit, SOAVersion, Document
from models import IncidentStatus, NCStatus
from app.models.task import Task, PeriodicTaskStatus
from app.models.change import Change, ChangeStatus
from app.risks.models import Riesgo
from datetime import datetime, timedelta
from sqlalchemy import func
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