from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import Risk, Incident, NonConformity, SOAControl, Audit, SOAVersion
from models import IncidentStatus, NCStatus
from app.models.task import Task, PeriodicTaskStatus
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

    # Risk metrics
    total_risks = Risk.query.count()
    high_risks = Risk.query.filter(Risk.risk_level.in_(['high', 'critical'])).count()
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