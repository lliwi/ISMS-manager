"""
Blueprint para Gestión de Auditorías
Control 9.2 - Auditoría interna del sistema de gestión de seguridad de la información
ISO 27001:2023 Clauses 9.2, 9.2.1, 9.2.2
ISO 19011:2018 - Directrices para la auditoría de sistemas de gestión
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from sqlalchemy import and_, or_
from datetime import datetime, date
from werkzeug.utils import secure_filename
import json
import os

from app.models.audit import (
    AuditRecord, AuditFinding, AuditCorrectiveAction, AuditProgram,
    AuditSchedule, AuditTeamMember, AuditDocument, DocumentType, AuditType, AuditStatus,
    FindingType, FindingStatus, AuditActionStatus, ProgramStatus
)
from app.services.audit_service import AuditService
from app.services.finding_service import FindingService
from app.services.corrective_action_service import CorrectiveActionService
from app.services.audit_program_service import AuditProgramService
from models import db, User, SOAControl

audits_bp = Blueprint('audits', __name__)

# Configuración de archivos permitidos
UPLOAD_FOLDER_AUDITS = 'uploads/audits'

# Inicializar servicios
audit_service = AuditService()
finding_service = FindingService()
action_service = CorrectiveActionService()
program_service = AuditProgramService()


# ==================== DASHBOARD Y VISTAS PRINCIPALES ====================

@audits_bp.route('/')
@login_required
def index():
    """Dashboard principal de auditorías"""
    try:
        # Obtener programa activo
        current_year = datetime.now().year
        active_program = AuditProgram.query.filter_by(
            year=current_year,
            status=ProgramStatus.APPROVED
        ).first()

        # Métricas generales
        total_audits = AuditRecord.query.filter(
            db.func.extract('year', AuditRecord.start_date) == current_year
        ).count()

        completed_audits = AuditRecord.query.filter(
            db.func.extract('year', AuditRecord.start_date) == current_year,
            AuditRecord.status.in_([AuditStatus.COMPLETED, AuditStatus.CLOSED])
        ).count()

        in_progress_audits = AuditRecord.query.filter(
            db.func.extract('year', AuditRecord.start_date) == current_year,
            AuditRecord.status.in_([AuditStatus.IN_PROGRESS, AuditStatus.PREPARATION])
        ).count()

        # Hallazgos abiertos
        open_findings = AuditFinding.query.filter(
            AuditFinding.status.in_([FindingStatus.OPEN, FindingStatus.IN_TREATMENT])
        ).count()

        # Hallazgos vencidos
        overdue_findings = finding_service.get_overdue_findings()

        # Acciones correctivas pendientes
        pending_actions = AuditCorrectiveAction.query.filter(
            AuditCorrectiveAction.status.in_([AuditActionStatus.PENDING, AuditActionStatus.IN_PROGRESS])
        ).count()

        # Verificaciones pendientes
        pending_verifications = action_service.get_pending_verifications()

        # Próximas auditorías (siguientes 30 días)
        from datetime import timedelta
        upcoming_audits = AuditRecord.query.filter(
            AuditRecord.start_date.between(
                datetime.now(),
                datetime.now() + timedelta(days=30)
            ),
            AuditRecord.status.in_([AuditStatus.PLANNED, AuditStatus.NOTIFIED])
        ).order_by(AuditRecord.start_date).limit(5).all()

        # Calcular tasas
        completion_rate = (completed_audits / total_audits * 100) if total_audits > 0 else 0

        # Cobertura ISO 27001
        iso_coverage = 0
        if active_program:
            iso_coverage = program_service.calculate_iso27001_coverage(active_program.id)

        return render_template('audits/dashboard.html',
            active_program=active_program,
            total_audits=total_audits,
            completed_audits=completed_audits,
            in_progress_audits=in_progress_audits,
            completion_rate=round(completion_rate, 1),
            open_findings=open_findings,
            overdue_findings_count=len(overdue_findings),
            pending_actions=pending_actions,
            pending_verifications_count=len(pending_verifications),
            upcoming_audits=upcoming_audits,
            iso_coverage=round(iso_coverage, 1),
            current_year=current_year
        )
    except Exception as e:
        flash(f'Error al cargar el dashboard: {str(e)}', 'error')
        # Pasar valores por defecto en caso de error
        return render_template('audits/dashboard.html',
            active_program=None,
            total_audits=0,
            completed_audits=0,
            in_progress_audits=0,
            completion_rate=0,
            open_findings=0,
            overdue_findings_count=0,
            pending_actions=0,
            pending_verifications_count=0,
            upcoming_audits=[],
            iso_coverage=0,
            current_year=datetime.now().year
        )


# ==================== GESTIÓN DE PROGRAMAS DE AUDITORÍA ====================

@audits_bp.route('/programas')
@login_required
def programs_list():
    """Listar programas de auditoría"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = AuditProgram.query.order_by(AuditProgram.year.desc())

        # Filtros
        year_filter = request.args.get('year', type=int)
        if year_filter:
            query = query.filter_by(year=year_filter)

        status_filter = request.args.get('status')
        if status_filter:
            query = query.filter_by(status=status_filter)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        programs = pagination.items

        return render_template('audits/programs/list.html',
            programs=programs,
            pagination=pagination,
            datetime=datetime
        )
    except Exception as e:
        flash(f'Error al cargar programas: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


@audits_bp.route('/programas/nuevo', methods=['GET', 'POST'])
@login_required
def program_create():
    """Crear nuevo programa de auditoría"""
    if request.method == 'POST':
        try:
            data = request.form.to_dict()

            # Procesar fechas
            if 'start_date' in data and data['start_date']:
                data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            if 'end_date' in data and data['end_date']:
                data['end_date'] = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

            # Procesar objetivos (lista de strings)
            objectives = request.form.getlist('objectives[]')
            if objectives:
                data['objectives'] = objectives

            program, errors = program_service.create_program(
                data=data,
                created_by_id=current_user.id
            )

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('audits/programs/form.html',
                    program=None,
                    suggestion=None,
                    datetime=datetime
                )

            flash(f'Programa de auditoría {program.year} creado exitosamente', 'success')
            return redirect(url_for('audits.program_detail', id=program.id))

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al crear programa: {str(e)}', 'error')

    # Sugerir programa basado en año anterior
    current_year = datetime.now().year
    suggestion = program_service.propose_program_from_previous_year(current_year)

    return render_template('audits/programs/form.html',
        program=None,
        suggestion=suggestion,
        datetime=datetime
    )


@audits_bp.route('/programas/<int:id>')
@login_required
def program_detail(id):
    """Ver detalle de programa de auditoría"""
    try:
        program = AuditProgram.query.get_or_404(id)

        # Obtener métricas del programa
        metrics = program_service.get_program_metrics(id)

        # Calcular cobertura ISO 27001
        iso_coverage = program_service.calculate_iso27001_coverage(id)

        # Obtener schedule items
        schedule_items = AuditSchedule.query.filter_by(
            audit_program_id=id
        ).order_by(AuditSchedule.next_planned_date).all()

        # Obtener auditorías asociadas
        audits = AuditRecord.query.filter_by(audit_program_id=id).all()

        return render_template('audits/programs/detail.html',
            program=program,
            metrics=metrics,
            iso_coverage=round(iso_coverage, 1),
            schedule_items=schedule_items,
            audits=audits
        )
    except Exception as e:
        flash(f'Error al cargar programa: {str(e)}', 'error')
        return redirect(url_for('audits.programs_list'))


@audits_bp.route('/programas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def program_edit(id):
    """Editar programa de auditoría"""
    program = AuditProgram.query.get_or_404(id)

    # No se puede editar programa aprobado
    if program.status == 'approved':
        flash('No se puede editar un programa aprobado', 'warning')
        return redirect(url_for('audits.program_detail', id=id))

    if request.method == 'POST':
        try:
            data = request.form.to_dict()

            # Procesar fechas
            if 'start_date' in data and data['start_date']:
                data['start_date'] = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            if 'end_date' in data and data['end_date']:
                data['end_date'] = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

            # Procesar objetivos
            objectives = request.form.getlist('objectives[]')
            if objectives:
                data['objectives'] = objectives

            program, errors = program_service.update_program(
                program_id=id,
                data=data,
                updated_by_id=current_user.id
            )

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('audits/programs/form.html',
                    program=program,
                    suggestion=None,
                    datetime=datetime
                )

            flash('Programa actualizado exitosamente', 'success')
            return redirect(url_for('audits.program_detail', id=id))

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al actualizar programa: {str(e)}', 'error')

    return render_template('audits/programs/form.html',
        program=program,
        datetime=datetime
    )


@audits_bp.route('/programas/<int:id>/aprobar', methods=['POST'])
@login_required
def program_approve(id):
    """Aprobar programa de auditoría"""
    try:
        success, errors = program_service.approve_program(
            program_id=id,
            approved_by_id=current_user.id
        )

        if not success:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('audits.program_detail', id=id))

        # Recargar el programa para obtener datos actualizados
        program = AuditProgram.query.get(id)
        flash(f'Programa {program.year} aprobado exitosamente', 'success')
        return redirect(url_for('audits.program_detail', id=id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audits.program_detail', id=id))
    except Exception as e:
        flash(f'Error al aprobar programa: {str(e)}', 'error')
        return redirect(url_for('audits.program_detail', id=id))


@audits_bp.route('/programas/<int:id>/generar-calendario', methods=['POST'])
@login_required
def program_generate_schedule(id):
    """Generar calendario de auditorías"""
    try:
        base_on_risks = request.form.get('base_on_risks', 'true') == 'true'

        schedule_items = program_service.generate_annual_schedule(
            program_id=id,
            base_on_risks=base_on_risks
        )

        flash(f'{len(schedule_items)} auditorías programadas exitosamente', 'success')
        return redirect(url_for('audits.program_detail', id=id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audits.program_detail', id=id))
    except Exception as e:
        flash(f'Error al generar calendario: {str(e)}', 'error')
        return redirect(url_for('audits.program_detail', id=id))


@audits_bp.route('/programas/<int:id>/eliminar', methods=['POST'])
@login_required
def program_delete(id):
    """Eliminar programa de auditoría (solo administradores)"""
    try:
        # Verificar que el usuario es administrador
        if not current_user.has_role('admin'):
            flash('Solo los administradores pueden eliminar programas de auditoría', 'error')
            return redirect(url_for('audits.program_detail', id=id))

        program = AuditProgram.query.get_or_404(id)

        # Verificar si tiene auditorías asociadas
        audits_count = program.audits.count()
        if audits_count > 0:
            flash(f'No se puede eliminar el programa. Tiene {audits_count} auditorías asociadas. Elimínelas primero.', 'warning')
            return redirect(url_for('audits.program_detail', id=id))

        # Verificar si tiene items de calendario
        schedule_count = program.schedules.count()
        if schedule_count > 0:
            # Eliminar items del calendario primero
            for schedule in program.schedules:
                db.session.delete(schedule)

        program_year = program.year
        db.session.delete(program)
        db.session.commit()

        flash(f'Programa de auditoría {program_year} eliminado exitosamente', 'success')
        return redirect(url_for('audits.programs_list'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar programa: {str(e)}', 'error')
        return redirect(url_for('audits.program_detail', id=id))


# ==================== GESTIÓN DE AUDITORÍAS ====================

@audits_bp.route('/auditorias')
@login_required
def audits_list():
    """Listar auditorías"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Construir filtros
        filters = {}

        if request.args.get('type'):
            filters['type'] = AuditType[request.args.get('type')]

        if request.args.get('status'):
            filters['status'] = AuditStatus[request.args.get('status')]

        if request.args.get('year'):
            filters['year'] = int(request.args.get('year'))

        if request.args.get('program_id'):
            filters['program_id'] = int(request.args.get('program_id'))

        if request.args.get('search'):
            filters['search'] = request.args.get('search')

        # Obtener auditorías con filtros
        pagination = audit_service.get_audits_list(
            filters=filters,
            page=page,
            per_page=per_page
        )

        return render_template('audits/audits/list.html',
            audits=pagination.items,
            total=pagination.total,
            page=page,
            per_page=per_page,
            total_pages=pagination.pages,
            pagination=pagination,
            datetime=datetime
        )
    except Exception as e:
        flash(f'Error al cargar auditorías: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


@audits_bp.route('/auditorias/nueva', methods=['GET', 'POST'])
@login_required
def audit_create():
    """Crear nueva auditoría"""
    if request.method == 'POST':
        try:
            data = request.form.to_dict()

            # Procesar fechas
            date_fields = ['planned_date', 'start_date', 'end_date', 'notification_date', 'report_date', 'closure_date']
            for field in date_fields:
                if field in data and data[field]:
                    try:
                        data[field] = datetime.strptime(data[field], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Ignorar fechas con formato inválido

            # Procesar áreas auditadas (lista)
            audited_areas = request.form.getlist('audited_areas[]')
            if audited_areas:
                data['audited_areas'] = json.dumps(audited_areas)

            # Procesar controles auditados (lista)
            audited_controls = request.form.getlist('audited_controls[]')
            if audited_controls:
                data['audited_controls'] = json.dumps(audited_controls)

            audit, errors = audit_service.create_audit(
                data=data,
                created_by_id=current_user.id,
                program_id=data.get('program_id')
            )

            if errors:
                for error in errors:
                    flash(error, 'error')
                # Reload data for form
                active_programs = AuditProgram.query.filter_by(status=ProgramStatus.APPROVED).all()
                if not active_programs:
                    active_programs = AuditProgram.query.order_by(AuditProgram.year.desc()).all()
                qualified_auditors = User.query.filter_by(is_active=True).all()
                qualified_auditors = sorted(qualified_auditors, key=lambda u: u.full_name or u.username)
                controls = SOAControl.query.filter_by(applicability_status='aplicable').order_by(SOAControl.control_id).all()
                return render_template('audits/audits/form.html',
                    programs=active_programs,
                    qualified_auditors=qualified_auditors,
                    controls=controls,
                    datetime=datetime
                )

            flash(f'Auditoría {audit.audit_code} creada exitosamente', 'success')
            return redirect(url_for('audits.audit_detail', id=audit.id))

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al crear auditoría: {str(e)}', 'error')

    # Obtener programas activos para el selector
    # Primero intentar obtener programas aprobados
    active_programs = AuditProgram.query.filter_by(status=ProgramStatus.APPROVED).all()

    # Si no hay programas aprobados, mostrar todos
    if not active_programs:
        active_programs = AuditProgram.query.order_by(AuditProgram.year.desc()).all()

    # Obtener usuarios que pueden ser auditores
    # Por ahora, todos los usuarios activos pueden ser auditores
    # TODO: filtrar por roles específicos (auditor, ciso, admin)
    qualified_auditors = User.query.filter_by(is_active=True).all()
    # Ordenar por nombre en Python ya que full_name es una propiedad
    qualified_auditors = sorted(qualified_auditors, key=lambda u: u.full_name or u.username)

    # Obtener controles SOA aplicables
    controls = SOAControl.query.filter_by(applicability_status='aplicable').order_by(SOAControl.control_id).all()

    return render_template('audits/audits/form.html',
        audit=None,
        active_programs=active_programs,
        programs=active_programs,
        qualified_auditors=qualified_auditors,
        organizational_areas=[],  # TODO: obtener áreas
        controls=controls,
        selected_controls=[],
        datetime=datetime
    )


@audits_bp.route('/auditorias/<int:id>')
@login_required
def audit_detail(id):
    """Ver detalle de auditoría"""
    try:
        audit = AuditRecord.query.get_or_404(id)

        # Calcular métricas
        conformity_rate = audit_service.calculate_conformity_rate(id)

        # Obtener hallazgos por tipo
        findings_by_type = db.session.query(
            AuditFinding.finding_type,
            db.func.count(AuditFinding.id)
        ).filter_by(audit_id=id).group_by(AuditFinding.finding_type).all()

        findings_stats = {
            'major_nc': 0,
            'minor_nc': 0,
            'observations': 0,
            'opportunities': 0
        }

        for finding_type, count in findings_by_type:
            if finding_type == FindingType.MAJOR_NC:
                findings_stats['major_nc'] = count
            elif finding_type == FindingType.MINOR_NC:
                findings_stats['minor_nc'] = count
            elif finding_type == FindingType.OBSERVATION:
                findings_stats['observations'] = count
            elif finding_type == FindingType.OPPORTUNITY_IMPROVEMENT:
                findings_stats['opportunities'] = count

        # Obtener usuarios calificados para agregar al equipo
        qualified_auditors = User.query.filter_by(is_active=True).all()
        qualified_auditors = sorted(qualified_auditors, key=lambda u: u.full_name or u.username)

        return render_template('audits/audits/detail.html',
            audit=audit,
            conformity_rate=round(conformity_rate, 1),
            findings_stats=findings_stats,
            qualified_auditors=qualified_auditors
        )
    except Exception as e:
        flash(f'Error al cargar auditoría: {str(e)}', 'error')
        return redirect(url_for('audits.audits_list'))


@audits_bp.route('/auditorias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def audit_edit(id):
    """Editar auditoría"""
    audit = AuditRecord.query.get_or_404(id)

    # No se puede editar auditoría cerrada
    if audit.status == AuditStatus.CLOSED:
        flash('No se puede editar una auditoría cerrada', 'warning')
        return redirect(url_for('audits.audit_detail', id=id))

    if request.method == 'POST':
        try:
            data = request.form.to_dict()

            # Procesar fechas
            date_fields = ['planned_date', 'start_date', 'end_date', 'notification_date', 'report_date', 'closure_date']
            for field in date_fields:
                if field in data and data[field]:
                    try:
                        data[field] = datetime.strptime(data[field], '%Y-%m-%d').date()
                    except ValueError:
                        pass  # Ignorar fechas con formato inválido

            # Procesar listas
            audited_areas = request.form.getlist('audited_areas[]')
            if audited_areas:
                data['audited_areas'] = json.dumps(audited_areas)

            audited_controls = request.form.getlist('audited_controls[]')
            if audited_controls:
                data['audited_controls'] = json.dumps(audited_controls)

            updated_audit, errors = audit_service.update_audit(
                audit_id=id,
                data=data,
                updated_by_id=current_user.id
            )

            if errors:
                for error in errors:
                    flash(error, 'error')
                # Reload audit and form data
                audit = AuditRecord.query.get_or_404(id)
                active_programs = AuditProgram.query.filter_by(status=ProgramStatus.APPROVED).all()
                if not active_programs:
                    active_programs = AuditProgram.query.order_by(AuditProgram.year.desc()).all()
                qualified_auditors = User.query.filter_by(is_active=True).all()
                qualified_auditors = sorted(qualified_auditors, key=lambda u: u.full_name or u.username)
                controls = SOAControl.query.filter_by(applicability_status='aplicable').order_by(SOAControl.control_id).all()
                return render_template('audits/audits/form.html',
                    audit=audit,
                    programs=active_programs,
                    qualified_auditors=qualified_auditors,
                    controls=controls,
                    datetime=datetime
                )

            flash('Auditoría actualizada exitosamente', 'success')
            return redirect(url_for('audits.audit_detail', id=id))

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al actualizar auditoría: {str(e)}', 'error')

    # Obtener programas activos
    active_programs = AuditProgram.query.filter_by(status=ProgramStatus.APPROVED).all()

    # Si no hay programas aprobados, mostrar todos
    if not active_programs:
        active_programs = AuditProgram.query.order_by(AuditProgram.year.desc()).all()

    # Obtener usuarios que pueden ser auditores
    qualified_auditors = User.query.filter_by(is_active=True).all()
    # Ordenar por nombre en Python ya que full_name es una propiedad
    qualified_auditors = sorted(qualified_auditors, key=lambda u: u.full_name or u.username)

    # Obtener controles SOA aplicables
    controls = SOAControl.query.filter_by(applicability_status='aplicable').order_by(SOAControl.control_id).all()

    # Parsear controles auditados desde JSON si existen
    selected_controls = []
    if audit and audit.audited_controls:
        try:
            if isinstance(audit.audited_controls, str):
                selected_controls = json.loads(audit.audited_controls)
            elif isinstance(audit.audited_controls, list):
                selected_controls = audit.audited_controls
            else:
                selected_controls = []
        except:
            selected_controls = []

    return render_template('audits/audits/form.html',
        audit=audit,
        active_programs=active_programs,
        programs=active_programs,
        qualified_auditors=qualified_auditors,
        organizational_areas=[],  # TODO: obtener áreas
        controls=controls,
        selected_controls=selected_controls,
        datetime=datetime
    )


@audits_bp.route('/auditorias/<int:id>/eliminar', methods=['POST'])
@login_required
def audit_delete(id):
    """Eliminar auditoría"""
    try:
        audit = AuditRecord.query.get_or_404(id)

        # Los administradores pueden eliminar cualquier auditoría
        is_admin = current_user.has_role('admin')

        # Usuarios normales solo pueden eliminar auditorías en estado PLANNED
        if not is_admin and audit.status != AuditStatus.PLANNED:
            flash('Solo se pueden eliminar auditorías en estado Planificada', 'warning')
            return redirect(url_for('audits.audit_detail', id=id))

        # Verificar si tiene hallazgos
        findings_count = len(audit.findings)
        if findings_count > 0 and not is_admin:
            flash(f'No se puede eliminar la auditoría. Tiene {findings_count} hallazgos asociados.', 'warning')
            return redirect(url_for('audits.audit_detail', id=id))

        # Si es admin y tiene hallazgos, eliminarlos en cascada
        if findings_count > 0 and is_admin:
            # Los hallazgos se eliminarán en cascada por la relación en el modelo
            pass

        audit_code = audit.audit_code
        db.session.delete(audit)
        db.session.commit()

        flash(f'Auditoría {audit_code} eliminada exitosamente', 'success')
        return redirect(url_for('audits.audits_list'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar auditoría: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


# ==================== TRANSICIONES DE ESTADO DE AUDITORÍA ====================

@audits_bp.route('/auditorias/<int:id>/notificar', methods=['POST'])
@login_required
def audit_notify(id):
    """Notificar auditoría (PLANNED → NOTIFIED)"""
    try:
        notes = request.form.get('notes')
        success, errors = audit_service.change_status(
            audit_id=id,
            new_status=AuditStatus.NOTIFIED,
            user_id=current_user.id,
            notes=notes
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        audit = AuditRecord.query.get(id)
        flash(f'Auditoría {audit.audit_code} notificada exitosamente', 'success')
        return redirect(url_for('audits.audit_detail', id=id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


@audits_bp.route('/auditorias/<int:id>/preparar', methods=['POST'])
@login_required
def audit_prepare(id):
    """Iniciar preparación (NOTIFIED → PREPARATION)"""
    try:
        notes = request.form.get('notes')
        success, errors = audit_service.change_status(
            audit_id=id,
            new_status=AuditStatus.PREPARATION,
            user_id=current_user.id,
            notes=notes
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        flash('Auditoría en preparación', 'success')
        return redirect(url_for('audits.audit_detail', id=id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


@audits_bp.route('/auditorias/<int:id>/iniciar', methods=['POST'])
@login_required
def audit_start(id):
    """Iniciar auditoría (PREPARATION → IN_PROGRESS)"""
    try:
        notes = request.form.get('notes')
        success, errors = audit_service.change_status(
            audit_id=id,
            new_status=AuditStatus.IN_PROGRESS,
            user_id=current_user.id,
            notes=notes
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        flash('Auditoría iniciada', 'success')
        return redirect(url_for('audits.audit_detail', id=id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


@audits_bp.route('/auditorias/<int:id>/reportar', methods=['POST'])
@login_required
def audit_report(id):
    """Pasar a fase de reporte (IN_PROGRESS → REPORTING)"""
    try:
        notes = request.form.get('notes')
        success, errors = audit_service.change_status(
            audit_id=id,
            new_status=AuditStatus.REPORTING,
            user_id=current_user.id,
            notes=notes
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        flash('Auditoría en fase de reporte', 'success')
        return redirect(url_for('audits.audit_detail', id=id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


@audits_bp.route('/auditorias/<int:id>/completar', methods=['POST'])
@login_required
def audit_complete(id):
    """Completar auditoría (REPORTING → COMPLETED)"""
    try:
        notes = request.form.get('notes')
        success, errors = audit_service.change_status(
            audit_id=id,
            new_status=AuditStatus.COMPLETED,
            user_id=current_user.id,
            notes=notes
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        audit = AuditRecord.query.get(id)
        flash(f'Auditoría {audit.audit_code} completada', 'success')
        return redirect(url_for('audits.audit_detail', id=id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


@audits_bp.route('/auditorias/<int:id>/cerrar', methods=['POST'])
@login_required
def audit_close(id):
    """Cerrar auditoría (COMPLETED → CLOSED)"""
    try:
        notes = request.form.get('notes')
        success, errors = audit_service.change_status(
            audit_id=id,
            new_status=AuditStatus.CLOSED,
            user_id=current_user.id,
            notes=notes
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        audit = AuditRecord.query.get(id)
        flash(f'Auditoría {audit.audit_code} cerrada', 'success')
        return redirect(url_for('audits.audit_detail', id=id))

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


# ==================== GESTIÓN DE EQUIPO DE AUDITORÍA ====================

@audits_bp.route('/auditorias/<int:id>/equipo/agregar', methods=['POST'])
@login_required
def audit_add_team_member(id):
    """Agregar miembro al equipo de auditoría"""
    try:
        user_id = int(request.form.get('user_id'))
        role = request.form.get('role')
        assigned_areas = request.form.getlist('assigned_areas[]')

        team_member, errors = audit_service.add_team_member(
            audit_id=id,
            user_id=user_id,
            role=role,
            assigned_by_id=current_user.id,
            assigned_areas=assigned_areas if assigned_areas else None
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        flash('Miembro agregado al equipo de auditoría', 'success')
        return redirect(url_for('audits.audit_detail', id=id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audits.audit_detail', id=id))
    except Exception as e:
        flash(f'Error al agregar miembro: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


@audits_bp.route('/auditorias/<int:audit_id>/equipo/<int:member_id>/eliminar', methods=['POST'])
@login_required
def audit_remove_team_member(audit_id, member_id):
    """Eliminar miembro del equipo de auditoría"""
    try:
        member = AuditTeamMember.query.get_or_404(member_id)

        if member.audit_id != audit_id:
            flash('Miembro no pertenece a esta auditoría', 'error')
            return redirect(url_for('audits.audit_detail', id=audit_id))

        audit_service.remove_team_member(member_id, current_user.id)

        flash('Miembro eliminado del equipo', 'success')
        return redirect(url_for('audits.audit_detail', id=audit_id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audits.audit_detail', id=audit_id))


# ==================== GESTIÓN DE HALLAZGOS ====================

@audits_bp.route('/auditorias/<int:id>/hallazgos')
@login_required
def audit_findings(id):
    """Listar hallazgos de una auditoría"""
    try:
        audit = AuditRecord.query.get_or_404(id)

        # Filtros
        status_filter = request.args.get('status')
        type_filter = request.args.get('type')

        query = AuditFinding.query.filter_by(audit_id=id)

        if status_filter:
            query = query.filter_by(status=FindingStatus[status_filter])

        if type_filter:
            query = query.filter_by(finding_type=FindingType[type_filter])

        findings = query.order_by(AuditFinding.finding_number).all()

        return render_template('audits/findings/list.html',
            audit=audit,
            findings=findings
        )
    except Exception as e:
        flash(f'Error al cargar hallazgos: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


@audits_bp.route('/auditorias/<int:id>/hallazgos/nuevo', methods=['GET', 'POST'])
@login_required
def finding_create(id):
    """Crear nuevo hallazgo"""
    audit = AuditRecord.query.get_or_404(id)

    if request.method == 'POST':
        try:
            data = request.form.to_dict()

            # Procesar controles afectados (lista)
            affected_controls = request.form.getlist('affected_controls[]')
            if affected_controls:
                data['affected_controls'] = affected_controls

            finding, errors = finding_service.create_finding(
                audit_id=id,
                data=data,
                created_by_id=current_user.id
            )

            if errors:
                for error in errors:
                    flash(error, 'error')
                # No redirigir, mostrar el formulario de nuevo con los errores
            elif finding:
                flash(f'Hallazgo {finding.finding_code} creado exitosamente', 'success')
                return redirect(url_for('audits.finding_detail', id=finding.id))
            else:
                flash('Error desconocido al crear hallazgo', 'error')

        except Exception as e:
            flash(f'Error al crear hallazgo: {str(e)}', 'error')

    # Obtener usuarios activos para el select de responsable
    users = User.query.filter_by(is_active=True).order_by(User.username).all()

    # Obtener controles SOA para referencia
    controls = SOAControl.query.filter_by(applicability_status='aplicable').order_by(SOAControl.control_id).all()

    return render_template('audits/findings/form.html',
        audit=audit,
        finding=None,
        users=users,
        controls=controls
    )


@audits_bp.route('/hallazgos/<int:id>')
@login_required
def finding_detail(id):
    """Ver detalle de hallazgo"""
    try:
        finding = AuditFinding.query.get_or_404(id)

        return render_template('audits/findings/detail.html',
            finding=finding
        )
    except Exception as e:
        flash(f'Error al cargar hallazgo: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


@audits_bp.route('/hallazgos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def finding_edit(id):
    """Editar hallazgo"""
    finding = AuditFinding.query.get_or_404(id)

    # No se puede editar hallazgo cerrado
    if finding.status == FindingStatus.CLOSED:
        flash('No se puede editar un hallazgo cerrado', 'warning')
        return redirect(url_for('audits.finding_detail', id=id))

    if request.method == 'POST':
        try:
            data = request.form.to_dict()

            affected_controls = request.form.getlist('affected_controls[]')
            if affected_controls:
                data['affected_controls'] = affected_controls

            finding, errors = finding_service.update_finding(
                finding_id=id,
                data=data,
                updated_by_id=current_user.id
            )

            if errors:
                for error in errors:
                    flash(error, 'error')
                # No redirigir, mostrar el formulario de nuevo con los errores
            elif finding:
                flash('Hallazgo actualizado exitosamente', 'success')
                return redirect(url_for('audits.finding_detail', id=id))
            else:
                flash('Error desconocido al actualizar hallazgo', 'error')

        except Exception as e:
            flash(f'Error al actualizar hallazgo: {str(e)}', 'error')

    # Obtener usuarios activos para el select de responsable
    users = User.query.filter_by(is_active=True).order_by(User.username).all()

    # Obtener controles SOA para referencia
    controls = SOAControl.query.filter_by(applicability_status='aplicable').order_by(SOAControl.control_id).all()

    return render_template('audits/findings/form.html',
        audit=finding.audit,
        finding=finding,
        users=users,
        controls=controls
    )


@audits_bp.route('/hallazgos/<int:id>/cerrar', methods=['POST'])
@login_required
def finding_close(id):
    """Cerrar hallazgo"""
    try:
        closure_notes = request.form.get('closure_notes')

        finding = finding_service.close_finding(
            finding_id=id,
            closed_by_id=current_user.id,
            closure_notes=closure_notes
        )

        flash(f'Hallazgo {finding.finding_code} cerrado exitosamente', 'success')
        return redirect(url_for('audits.finding_detail', id=id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audits.finding_detail', id=id))


@audits_bp.route('/hallazgos/<int:id>/reabrir', methods=['POST'])
@login_required
def finding_reopen(id):
    """Reabrir hallazgo"""
    try:
        reason = request.form.get('reason')

        if not reason:
            flash('Debe proporcionar una razón para reabrir el hallazgo', 'error')
            return redirect(url_for('audits.finding_detail', id=id))

        finding = finding_service.reopen_finding(
            finding_id=id,
            reopened_by_id=current_user.id,
            reason=reason
        )

        flash(f'Hallazgo {finding.finding_code} reabierto', 'success')
        return redirect(url_for('audits.finding_detail', id=id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audits.finding_detail', id=id))


# ==================== GESTIÓN DE ACCIONES CORRECTIVAS ====================

@audits_bp.route('/hallazgos/<int:id>/acciones/nueva', methods=['GET', 'POST'])
@login_required
def action_create(id):
    """Crear nueva acción correctiva"""
    finding = AuditFinding.query.get_or_404(id)

    if request.method == 'POST':
        try:
            data = request.form.to_dict()

            # Procesar fechas
            if 'planned_completion_date' in data:
                data['planned_completion_date'] = datetime.strptime(
                    data['planned_completion_date'], '%Y-%m-%d'
                ).date()

            # Procesar costo estimado
            if 'estimated_cost' in data and data['estimated_cost']:
                data['estimated_cost'] = float(data['estimated_cost'])

            action, errors = action_service.create_action(
                finding_id=id,
                data=data,
                created_by_id=current_user.id
            )

            if errors:
                for error in errors:
                    flash(error, 'error')
            elif action:
                flash(f'Acción correctiva {action.action_code} creada exitosamente', 'success')
                return redirect(url_for('audits.finding_detail', id=id))
            else:
                flash('Error desconocido al crear acción correctiva', 'error')

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al crear acción: {str(e)}', 'error')

    # Cargar usuarios activos para los selects
    users = User.query.filter_by(is_active=True).order_by(User.username).all()

    # Fecha mínima (mañana)
    from datetime import timedelta
    min_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')

    return render_template('audits/actions/form.html',
        finding=finding,
        action=None,
        users=users,
        min_date=min_date
    )


@audits_bp.route('/acciones/<int:id>')
@login_required
def action_detail(id):
    """Ver detalle de acción correctiva"""
    try:
        action = AuditCorrectiveAction.query.get_or_404(id)

        return render_template('audits/actions/detail.html',
            action=action
        )
    except Exception as e:
        flash(f'Error al cargar acción: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


@audits_bp.route('/acciones/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def action_edit(id):
    """Editar acción correctiva"""
    action = AuditCorrectiveAction.query.get_or_404(id)

    # No se puede editar acción completada o verificada
    if action.status in [AuditActionStatus.COMPLETED, AuditActionStatus.VERIFIED]:
        flash('No se puede editar una acción completada o verificada', 'warning')
        return redirect(url_for('audits.action_detail', id=id))

    if request.method == 'POST':
        try:
            data = request.form.to_dict()

            if 'planned_completion_date' in data:
                data['planned_completion_date'] = datetime.strptime(
                    data['planned_completion_date'], '%Y-%m-%d'
                ).date()

            if 'estimated_cost' in data and data['estimated_cost']:
                data['estimated_cost'] = float(data['estimated_cost'])

            action, errors = action_service.update_action(
                action_id=id,
                data=data,
                updated_by_id=current_user.id
            )

            if errors:
                for error in errors:
                    flash(error, 'error')
            elif action:
                flash(f'Acción {action.action_code} actualizada exitosamente', 'success')
                return redirect(url_for('audits.action_detail', id=id))
            else:
                flash('Error desconocido al actualizar acción', 'error')

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error al actualizar acción: {str(e)}', 'error')

    # Cargar usuarios activos para los selects
    users = User.query.filter_by(is_active=True).order_by(User.username).all()

    # Fecha mínima (mañana)
    from datetime import timedelta
    min_date = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')

    return render_template('audits/actions/form.html',
        finding=action.finding,
        action=action,
        users=users,
        min_date=min_date
    )


@audits_bp.route('/acciones/<int:id>/progreso', methods=['POST'])
@login_required
def action_update_progress(id):
    """Actualizar progreso de acción"""
    try:
        progress = int(request.form.get('progress', 0))
        notes = request.form.get('notes')

        action = action_service.update_progress(
            action_id=id,
            progress_percentage=progress,
            notes=notes,
            updated_by_id=current_user.id
        )

        flash('Progreso actualizado exitosamente', 'success')
        return redirect(url_for('audits.action_detail', id=id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audits.action_detail', id=id))


@audits_bp.route('/acciones/<int:id>/completar', methods=['POST'])
@login_required
def action_complete(id):
    """Completar acción correctiva"""
    try:
        completion_notes = request.form.get('completion_notes')
        actual_cost = request.form.get('actual_cost')

        if actual_cost:
            actual_cost = float(actual_cost)

        action = action_service.complete_action(
            action_id=id,
            completed_by_id=current_user.id,
            completion_notes=completion_notes,
            actual_cost=actual_cost
        )

        flash('Acción completada exitosamente', 'success')
        return redirect(url_for('audits.action_detail', id=id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audits.action_detail', id=id))


@audits_bp.route('/acciones/<int:id>/verificar', methods=['POST'])
@login_required
def action_verify(id):
    """Verificar efectividad de acción"""
    try:
        is_effective = request.form.get('is_effective') == 'true'
        verification_notes = request.form.get('verification_notes')

        if not verification_notes:
            flash('Debe proporcionar notas de verificación', 'error')
            return redirect(url_for('audits.action_detail', id=id))

        action = action_service.verify_effectiveness(
            action_id=id,
            verifier_id=current_user.id,
            is_effective=is_effective,
            verification_notes=verification_notes
        )

        status_msg = 'efectiva' if is_effective else 'inefectiva'
        flash(f'Acción verificada como {status_msg}', 'success')
        return redirect(url_for('audits.action_detail', id=id))

    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('audits.action_detail', id=id))


# ==================== REPORTES Y ANALÍTICA ====================

@audits_bp.route('/reportes/hallazgos-vencidos')
@login_required
def report_overdue_findings():
    """Reporte de hallazgos vencidos"""
    try:
        overdue = finding_service.get_overdue_findings()

        return render_template('audits/reports/overdue_findings.html',
            findings=overdue
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


@audits_bp.route('/reportes/recurrencia')
@login_required
def report_recurrence():
    """Análisis de recurrencia de hallazgos"""
    try:
        analysis = finding_service.get_recurrence_analysis()

        return render_template('audits/reports/recurrence.html',
            analysis=analysis
        )
    except Exception as e:
        flash(f'Error al generar análisis: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


@audits_bp.route('/reportes/acciones-vencidas')
@login_required
def report_overdue_actions():
    """Reporte de acciones vencidas"""
    try:
        overdue = action_service.get_overdue_actions()

        return render_template('audits/reports/overdue_actions.html',
            actions=overdue
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


@audits_bp.route('/reportes/verificaciones-pendientes')
@login_required
def report_pending_verifications():
    """Reporte de verificaciones pendientes"""
    try:
        pending = action_service.get_pending_verifications()

        return render_template('audits/reports/pending_verifications.html',
            actions=pending
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


@audits_bp.route('/reportes/efectividad')
@login_required
def report_effectiveness():
    """Reporte de efectividad de acciones"""
    try:
        effectiveness_rate = action_service.calculate_effectiveness_rate()

        # Obtener todas las acciones verificadas (con verificación de efectividad)
        verified_actions = AuditCorrectiveAction.query.filter(
            AuditCorrectiveAction.status == AuditActionStatus.VERIFIED,
            AuditCorrectiveAction.effectiveness_verification_date.isnot(None)
        ).order_by(AuditCorrectiveAction.effectiveness_verification_date.desc()).all()

        return render_template('audits/reports/effectiveness.html',
            effectiveness_rate=round(effectiveness_rate, 1),
            actions=verified_actions
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


# ==================== API ENDPOINTS ====================

@audits_bp.route('/api/calendar/<int:program_id>')
@login_required
def api_calendar_events(program_id):
    """API: Obtener eventos de calendario para un programa"""
    try:
        events = program_service.get_calendar_events(program_id)
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@audits_bp.route('/api/audits/<int:id>/metrics')
@login_required
def api_audit_metrics(id):
    """API: Obtener métricas de una auditoría"""
    try:
        conformity_rate = audit_service.calculate_conformity_rate(id)

        audit = AuditRecord.query.get_or_404(id)

        return jsonify({
            'conformity_rate': round(conformity_rate, 1),
            'total_findings': audit.total_findings_count,
            'major_nc_count': audit.major_nc_count,
            'minor_nc_count': audit.minor_nc_count,
            'observations_count': audit.observations_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@audits_bp.route('/api/programs/<int:id>/coverage')
@login_required
def api_program_coverage(id):
    """API: Calcular cobertura ISO 27001 de un programa"""
    try:
        coverage = program_service.calculate_iso27001_coverage(id)
        return jsonify({'coverage': round(coverage, 1)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== GESTIÓN DE DOCUMENTOS ====================

def allowed_file(filename):
    """Verificar si la extensión del archivo es permitida"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@audits_bp.route('/auditorias/<int:id>/documentos/subir', methods=['POST'])
@login_required
def audit_upload_document(id):
    """Subir documento a una auditoría"""
    try:
        audit = AuditRecord.query.get_or_404(id)

        # Verificar que la auditoría no esté cerrada o cancelada
        if audit.status in [AuditStatus.CLOSED, AuditStatus.CANCELLED]:
            flash('No se pueden subir documentos a una auditoría cerrada o cancelada', 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        # Verificar que se haya subido un archivo
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        file = request.files['file']

        if file.filename == '':
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        if not allowed_file(file.filename):
            flash('Tipo de archivo no permitido. Use: PDF, DOC, DOCX, XLS, XLSX, TXT, PNG, JPG', 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        # Obtener datos del formulario
        document_type_str = request.form.get('document_type')
        title = request.form.get('title', file.filename)
        description = request.form.get('description', '')
        version = request.form.get('version', '1.0')
        is_final = request.form.get('is_final', 'false') == 'true'

        # Validar tipo de documento
        try:
            document_type = DocumentType[document_type_str]
        except KeyError:
            flash('Tipo de documento inválido', 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        # Generar nombre de archivo seguro
        filename = secure_filename(file.filename)
        if not filename:
            flash('Nombre de archivo inválido', 'error')
            return redirect(url_for('audits.audit_detail', id=id))

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"

        # Crear carpeta específica para esta auditoría
        audit_folder = os.path.join(UPLOAD_FOLDER_AUDITS, str(audit.id))
        os.makedirs(audit_folder, exist_ok=True)

        # Ruta completa del archivo
        file_path = os.path.join(audit_folder, unique_filename)

        # Guardar archivo
        file.save(file_path)

        document = AuditDocument(
            audit_id=id,
            document_type=document_type,
            title=title,
            description=description,
            file_path=file_path,  # Guardar la ruta relativa
            version=version,
            is_final=is_final,
            uploaded_by_id=current_user.id,
            upload_date=datetime.utcnow()
        )

        db.session.add(document)
        db.session.commit()

        flash(f'Documento "{title}" subido exitosamente', 'success')
        return redirect(url_for('audits.audit_detail', id=id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al subir documento: {str(e)}', 'error')
        return redirect(url_for('audits.audit_detail', id=id))


@audits_bp.route('/auditorias/documentos/<int:doc_id>/descargar')
@login_required
def audit_download_document(doc_id):
    """Descargar documento de auditoría"""
    try:
        document = AuditDocument.query.get_or_404(doc_id)

        if not document.file_path or not os.path.exists(document.file_path):
            flash('El archivo no existe', 'error')
            return redirect(url_for('audits.audit_detail', id=document.audit_id))

        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=os.path.basename(document.file_path)
        )

    except Exception as e:
        flash(f'Error al descargar documento: {str(e)}', 'error')
        return redirect(url_for('audits.index'))


@audits_bp.route('/auditorias/documentos/<int:doc_id>/eliminar', methods=['POST'])
@login_required
def audit_delete_document(doc_id):
    """Eliminar documento de auditoría"""
    try:
        document = AuditDocument.query.get_or_404(doc_id)
        audit_id = document.audit_id
        audit = document.audit

        # Verificar permisos
        if audit.status in [AuditStatus.CLOSED, AuditStatus.CANCELLED]:
            if not current_user.has_role('admin'):
                flash('No se pueden eliminar documentos de una auditoría cerrada', 'error')
                return redirect(url_for('audits.audit_detail', id=audit_id))

        # Eliminar archivo físico
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Eliminar registro de base de datos
        db.session.delete(document)
        db.session.commit()

        flash('Documento eliminado exitosamente', 'success')
        return redirect(url_for('audits.audit_detail', id=audit_id))

    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar documento: {str(e)}', 'error')
        return redirect(url_for('audits.index'))
