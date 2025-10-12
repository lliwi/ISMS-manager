from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Risk, Incident, NonConformity, Task, SOAControl, Audit
from models import IncidentStatus, NCStatus
from datetime import datetime, timedelta
from sqlalchemy import func

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
        Task.status != 'completed'
    ).count()
    pending_tasks = Task.query.filter_by(assignee_id=current_user.id, status='pending').count()
    kpis['overdue_tasks'] = overdue_tasks
    kpis['my_pending_tasks'] = pending_tasks

    # Recent activity
    recent_incidents = Incident.query.order_by(Incident.created_at.desc()).limit(5).all()
    recent_nonconformities = NonConformity.query.order_by(NonConformity.created_at.desc()).limit(5).all()
    my_tasks = Task.query.filter_by(assignee_id=current_user.id, status='pending').order_by(Task.due_date).limit(5).all()

    return render_template('dashboard/index.html',
                         kpis=kpis,
                         recent_incidents=recent_incidents,
                         recent_nonconformities=recent_nonconformities,
                         my_tasks=my_tasks,
                         current_datetime=datetime.utcnow())