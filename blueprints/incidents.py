from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Incident, User, db
from datetime import datetime

incidents_bp = Blueprint('incidents', __name__)

@incidents_bp.route('/')
@login_required
def index():
    incidents = Incident.query.order_by(Incident.detection_date.desc()).all()
    return render_template('incidents/index.html', incidents=incidents)

@incidents_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        incident = Incident(
            title=request.form['title'],
            description=request.form['description'],
            severity=request.form['severity'],
            incident_type=request.form['incident_type'],
            detection_date=datetime.strptime(request.form['detection_date'], '%Y-%m-%dT%H:%M'),
            reporter_id=current_user.id
        )

        db.session.add(incident)
        db.session.commit()

        flash('Incidente reportado correctamente', 'success')
        return redirect(url_for('incidents.view', id=incident.id))

    return render_template('incidents/create.html')

@incidents_bp.route('/<int:id>')
@login_required
def view(id):
    incident = Incident.query.get_or_404(id)
    return render_template('incidents/view.html', incident=incident)