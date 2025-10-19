"""
Servicio para Gestión de Auditorías
ISO 27001:2022 - Cláusula 9.2 (Auditoría interna)
"""
from datetime import datetime, timedelta
from sqlalchemy import func, or_
from app.models.audit import (
    AuditRecord, AuditProgram, AuditTeamMember, AuditDocument,
    AuditEvidence, AuditChecklist, AuditStatus, AuditType,
    AuditorRole, DocumentType, EvidenceType, AuditConclusion
)
from models import db, User
import json


class AuditService:
    """Servicio principal para gestión de auditorías"""

    @staticmethod
    def create_audit(data, created_by_id, program_id=None):
        """
        Crea una nueva auditoría

        Args:
            data: Diccionario con datos de la auditoría
            created_by_id: ID del usuario que crea la auditoría
            program_id: ID del programa de auditoría (opcional)

        Returns:
            tuple: (audit, errors)
        """
        errors = AuditService.validate_create(data)
        if errors:
            return None, errors

        try:
            # Generar código único
            audit_code = AuditRecord.generate_audit_code()

            # Crear auditoría
            audit = AuditRecord(
                audit_code=audit_code,
                title=data['title'],
                audit_type=AuditType[data['audit_type']],
                status=AuditStatus.PLANNED,
                scope=data['scope'],
                audit_criteria=data.get('audit_criteria', ''),
                objectives=data.get('objectives', ''),
                lead_auditor_id=data['lead_auditor_id'],
                planned_date=data.get('planned_date'),
                notification_date=data.get('notification_date'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                report_date=data.get('report_date'),
                closure_date=data.get('closure_date'),
                audited_areas=data.get('audited_areas', ''),
                audited_controls=data.get('audited_controls', ''),
                created_by_id=created_by_id,
                audit_program_id=program_id
            )

            db.session.add(audit)
            db.session.commit()

            # Agregar auditor líder al equipo
            AuditService.add_team_member(
                audit.id,
                data['lead_auditor_id'],
                AuditorRole.LEAD_AUDITOR,
                created_by_id
            )

            return audit, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al crear auditoría: {str(e)}"]

    @staticmethod
    def validate_create(data):
        """Valida datos para crear auditoría"""
        errors = []

        # Campos obligatorios
        required_fields = ['title', 'audit_type', 'scope', 'lead_auditor_id']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"El campo '{field}' es obligatorio")

        # Validar auditor líder
        if data.get('lead_auditor_id'):
            lead_auditor = User.query.get(data['lead_auditor_id'])
            if not lead_auditor:
                errors.append("Auditor líder no encontrado")

        # Validar fechas
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                errors.append("La fecha de inicio debe ser anterior a la fecha de fin")

        return errors

    @staticmethod
    def update_audit(audit_id, data, updated_by_id):
        """Actualiza una auditoría existente"""
        audit = AuditRecord.query.get(audit_id)
        if not audit:
            return None, ["Auditoría no encontrada"]

        try:
            # Actualizar campos
            if 'title' in data:
                audit.title = data['title']
            if 'scope' in data:
                audit.scope = data['scope']
            if 'audit_criteria' in data:
                audit.audit_criteria = data['audit_criteria']
            if 'objectives' in data:
                audit.objectives = data['objectives']
            if 'planned_date' in data:
                audit.planned_date = data['planned_date']
            if 'notification_date' in data:
                audit.notification_date = data['notification_date']
            if 'start_date' in data:
                audit.start_date = data['start_date']
            if 'end_date' in data:
                audit.end_date = data['end_date']
            if 'report_date' in data:
                audit.report_date = data['report_date']
            if 'closure_date' in data:
                audit.closure_date = data['closure_date']
            if 'audited_areas' in data:
                audit.audited_areas = data['audited_areas']
            if 'audited_controls' in data:
                audit.audited_controls = data['audited_controls']

            audit.updated_by_id = updated_by_id
            audit.updated_at = datetime.utcnow()

            db.session.commit()
            return audit, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al actualizar auditoría: {str(e)}"]

    @staticmethod
    def change_status(audit_id, new_status, user_id, notes=None):
        """
        Cambia el estado de una auditoría con validaciones

        Args:
            audit_id: ID de la auditoría
            new_status: Nuevo estado (AuditStatus)
            user_id: ID del usuario que realiza el cambio
            notes: Notas opcionales del cambio

        Returns:
            tuple: (success, errors)
        """
        audit = AuditRecord.query.get(audit_id)
        if not audit:
            return False, ["Auditoría no encontrada"]

        # Validar transición de estado
        errors = AuditService.validate_status_transition(audit, new_status)
        if errors:
            return False, errors

        try:
            old_status = audit.status
            audit.status = new_status
            audit.updated_by_id = user_id
            audit.updated_at = datetime.utcnow()

            # Actualizar fechas según el estado
            if new_status == AuditStatus.NOTIFIED:
                audit.notification_date = datetime.utcnow().date()
            elif new_status == AuditStatus.IN_PROGRESS:
                if not audit.start_date:
                    audit.start_date = datetime.utcnow().date()
            elif new_status == AuditStatus.COMPLETED:
                audit.end_date = datetime.utcnow().date()
                audit.report_date = datetime.utcnow().date()
            elif new_status == AuditStatus.CLOSED:
                audit.closure_date = datetime.utcnow().date()

            db.session.commit()

            # TODO: Registrar en audit_log
            # TODO: Enviar notificaciones

            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al cambiar estado: {str(e)}"]

    @staticmethod
    def validate_status_transition(audit, new_status):
        """Valida si la transición de estado es permitida"""
        errors = []

        # Definir transiciones permitidas
        allowed_transitions = {
            AuditStatus.PLANNED: [AuditStatus.NOTIFIED, AuditStatus.CANCELLED],
            AuditStatus.NOTIFIED: [AuditStatus.PREPARATION, AuditStatus.CANCELLED],
            AuditStatus.PREPARATION: [AuditStatus.IN_PROGRESS, AuditStatus.CANCELLED],
            AuditStatus.IN_PROGRESS: [AuditStatus.REPORTING],
            AuditStatus.REPORTING: [AuditStatus.COMPLETED],
            AuditStatus.COMPLETED: [AuditStatus.CLOSED],
            AuditStatus.CLOSED: [],
            AuditStatus.CANCELLED: []
        }

        current_status = audit.status
        if new_status not in allowed_transitions.get(current_status, []):
            errors.append(
                f"Transición no permitida: {current_status.value} → {new_status.value}"
            )

        # Validaciones específicas por estado
        if new_status == AuditStatus.IN_PROGRESS:
            # TODO: Reactivar cuando se implemente carga de documentos
            # if not audit.audit_plan_file:
            #     errors.append("Debe cargar el plan de auditoría antes de iniciar")
            if len(audit.team_members) == 0:
                errors.append("Debe asignar equipo auditor antes de iniciar")

        if new_status == AuditStatus.COMPLETED:
            # TODO: Reactivar cuando se implemente generación de informes
            # if not audit.audit_report_file:
            #     errors.append("Debe generar el informe antes de completar")
            pass

            # Verificar que hallazgos mayores tengan plan de acción
            from app.models.audit import FindingType
            major_findings = [f for f in audit.findings if f.finding_type == FindingType.MAJOR_NC]

            for finding in major_findings:
                if len(finding.corrective_actions) == 0:
                    errors.append(
                        f"Hallazgo {finding.finding_code} no tiene plan de acción"
                    )

        if new_status == AuditStatus.CLOSED:
            from app.models.audit import FindingStatus
            open_findings = [f for f in audit.findings if f.status != FindingStatus.CLOSED]
            if len(open_findings) > 0:
                errors.append(f"Quedan {len(open_findings)} hallazgos sin cerrar")

        return errors

    @staticmethod
    def add_team_member(audit_id, user_id, role, assigned_by_id, assigned_areas=None):
        """Agrega un miembro al equipo auditor"""
        audit = AuditRecord.query.get(audit_id)
        if not audit:
            return None, ["Auditoría no encontrada"]

        # Validar independencia
        errors = AuditService.validate_team_member_independence(
            user_id, audit.audited_areas
        )
        if errors:
            return None, errors

        # Verificar si ya está en el equipo
        existing = AuditTeamMember.query.filter_by(
            audit_id=audit_id,
            user_id=user_id
        ).first()

        if existing:
            return None, ["El usuario ya es miembro del equipo"]

        try:
            # Convertir role string a enum si es necesario
            if isinstance(role, str):
                try:
                    role_enum = AuditorRole[role]
                except KeyError:
                    return None, [f"Rol inválido: {role}"]
            else:
                role_enum = role

            member = AuditTeamMember(
                audit_id=audit_id,
                user_id=user_id,
                role=role_enum,
                assigned_areas=assigned_areas,
                is_independent=True
            )

            db.session.add(member)
            db.session.commit()

            return member, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al agregar miembro: {str(e)}"]

    @staticmethod
    def remove_team_member(audit_id, user_id):
        """Elimina un miembro del equipo auditor"""
        member = AuditTeamMember.query.filter_by(
            audit_id=audit_id,
            user_id=user_id
        ).first()

        if not member:
            return False, ["Miembro no encontrado en el equipo"]

        # No permitir eliminar al auditor líder
        audit = AuditRecord.query.get(audit_id)
        if audit.lead_auditor_id == user_id:
            return False, ["No se puede eliminar al auditor líder"]

        try:
            db.session.delete(member)
            db.session.commit()
            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al eliminar miembro: {str(e)}"]

    @staticmethod
    def validate_team_member_independence(user_id, audited_areas):
        """Valida la independencia del auditor respecto al área auditada"""
        errors = []

        user = User.query.get(user_id)
        if not user:
            errors.append("Usuario no encontrado")
            return errors

        # Verificar que no audite su propia área
        if audited_areas:
            try:
                areas = json.loads(audited_areas) if isinstance(audited_areas, str) else audited_areas
                if user.department in areas:
                    errors.append(
                        f"{user.full_name} no puede auditar su propia área ({user.department})"
                    )
            except:
                pass

        # Verificar calificación (DESHABILITADO - permitir cualquier usuario)
        # if not AuditService.is_qualified_auditor(user_id):
        #     errors.append(f"{user.full_name} no tiene calificación de auditor")

        return errors

    @staticmethod
    def is_qualified_auditor(user_id):
        """Verifica si un usuario tiene calificación de auditor"""
        from app.models.audit import AuditorQualification

        qualifications = AuditorQualification.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()

        # Verificar que tenga al menos una calificación vigente
        for qual in qualifications:
            if qual.expiry_date and qual.expiry_date >= datetime.now().date():
                return True
            elif not qual.expiry_date:  # Sin fecha de expiración
                return True

        return False

    @staticmethod
    def is_qualified_lead_auditor(user_id):
        """Verifica si un usuario tiene calificación de auditor líder"""
        from app.models.audit import AuditorQualification, QualificationType

        qualification = AuditorQualification.query.filter_by(
            user_id=user_id,
            qualification_type=QualificationType.LEAD_AUDITOR,
            is_active=True
        ).first()

        if not qualification:
            return False

        # Verificar vigencia
        if qualification.expiry_date:
            return qualification.expiry_date >= datetime.now().date()

        return True

    @staticmethod
    def calculate_conformity_rate(audit_id):
        """Calcula el porcentaje de conformidad de una auditoría"""
        audit = AuditRecord.query.get(audit_id)
        if not audit:
            return 0

        # Obtener checklists completados
        checklists = audit.checklists
        if not checklists:
            return 0

        total_items = 0
        conformant_items = 0

        for checklist in checklists:
            if checklist.items_data:
                try:
                    items = json.loads(checklist.items_data)
                    for item in items:
                        total_items += 1
                        if item.get('result') == 'conformant':
                            conformant_items += 1
                except:
                    pass

        if total_items == 0:
            return 0

        rate = (conformant_items / total_items) * 100

        # Actualizar en la auditoría
        audit.conformity_percentage = round(rate, 2)
        db.session.commit()

        return round(rate, 2)

    @staticmethod
    def get_audits_list(filters=None, page=1, per_page=20):
        """
        Obtiene lista de auditorías con filtros

        Args:
            filters: Diccionario con filtros (status, type, year, program_id)
            page: Número de página
            per_page: Resultados por página

        Returns:
            Pagination object
        """
        query = AuditRecord.query

        if filters:
            if filters.get('status'):
                query = query.filter(AuditRecord.status == filters['status'])

            if filters.get('audit_type'):
                query = query.filter(AuditRecord.audit_type == filters['audit_type'])

            if filters.get('year'):
                year = int(filters['year'])
                start_date = datetime(year, 1, 1)
                end_date = datetime(year, 12, 31)
                query = query.filter(
                    AuditRecord.planned_date.between(start_date, end_date)
                )

            if filters.get('program_id'):
                query = query.filter(
                    AuditRecord.audit_program_id == filters['program_id']
                )

            if filters.get('lead_auditor_id'):
                query = query.filter(
                    AuditRecord.lead_auditor_id == filters['lead_auditor_id']
                )

            if filters.get('search'):
                search = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        AuditRecord.audit_code.like(search),
                        AuditRecord.title.like(search)
                    )
                )

        # Ordenar por fecha de creación descendente
        query = query.order_by(AuditRecord.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_audit_summary(audit_id):
        """Obtiene resumen ejecutivo de una auditoría"""
        audit = AuditRecord.query.get(audit_id)
        if not audit:
            return None

        audit.update_findings_count()

        return {
            'audit_code': audit.audit_code,
            'title': audit.title,
            'status': audit.status.value,
            'type': audit.audit_type.value,
            'lead_auditor': audit.lead_auditor.full_name if audit.lead_auditor else None,
            'team_size': len(audit.team_members),
            'planned_date': audit.planned_date,
            'start_date': audit.start_date,
            'end_date': audit.end_date,
            'total_findings': audit.total_findings,
            'major_ncs': audit.major_findings_count,
            'minor_ncs': audit.minor_findings_count,
            'observations': audit.observations_count,
            'opportunities': audit.opportunities_count,
            'conformity_rate': audit.conformity_percentage,
            'overall_conclusion': audit.overall_conclusion.value if audit.overall_conclusion else None
        }

    @staticmethod
    def upload_document(audit_id, document_type, file, uploaded_by_id,
                       title=None, description=None):
        """Sube un documento a la auditoría"""
        audit = AuditRecord.query.get(audit_id)
        if not audit:
            return None, ["Auditoría no encontrada"]

        # TODO: Implementar validación de archivo
        # TODO: Guardar archivo físicamente

        try:
            document = AuditDocument(
                audit_id=audit_id,
                document_type=document_type,
                title=title or file.filename,
                description=description,
                file_path=f"/uploads/audits/{audit.audit_code}/{file.filename}",
                uploaded_by_id=uploaded_by_id
            )

            db.session.add(document)

            # Actualizar referencias en la auditoría
            if document_type == DocumentType.AUDIT_PLAN:
                audit.audit_plan_file = document.file_path
            elif document_type == DocumentType.AUDIT_REPORT:
                audit.audit_report_file = document.file_path

            db.session.commit()

            return document, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al subir documento: {str(e)}"]

    @staticmethod
    def get_audit_metrics(program_id=None, period='year'):
        """Obtiene métricas de auditorías"""
        query = AuditRecord.query

        if program_id:
            query = query.filter_by(audit_program_id=program_id)

        # Filtrar por período
        if period == 'year':
            start_date = datetime.now().replace(month=1, day=1)
        elif period == 'quarter':
            current_quarter = (datetime.now().month - 1) // 3
            start_date = datetime.now().replace(
                month=current_quarter * 3 + 1, day=1
            )
        else:  # month
            start_date = datetime.now().replace(day=1)

        query = query.filter(AuditRecord.created_at >= start_date)

        audits = query.all()

        total = len(audits)
        completed = len([a for a in audits if a.status in [
            AuditStatus.COMPLETED, AuditStatus.CLOSED
        ]])
        in_progress = len([a for a in audits if a.status == AuditStatus.IN_PROGRESS])

        total_findings = sum(a.total_findings for a in audits)
        major_ncs = sum(a.major_findings_count for a in audits)
        minor_ncs = sum(a.minor_findings_count for a in audits)

        return {
            'total_audits': total,
            'completed_audits': completed,
            'in_progress_audits': in_progress,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 2),
            'total_findings': total_findings,
            'major_ncs': major_ncs,
            'minor_ncs': minor_ncs,
            'average_findings_per_audit': round(total_findings / total, 2) if total > 0 else 0
        }

    @staticmethod
    def notify_audit(audit_id, notification_date=None):
        """Notifica el inicio de una auditoría al área auditada"""
        audit = AuditRecord.query.get(audit_id)
        if not audit:
            return False, ["Auditoría no encontrada"]

        if audit.status != AuditStatus.PLANNED:
            return False, ["Solo se pueden notificar auditorías planificadas"]

        try:
            # Cambiar estado
            success, errors = AuditService.change_status(
                audit_id,
                AuditStatus.NOTIFIED,
                audit.lead_auditor_id,
                "Auditoría notificada al área auditada"
            )

            if not success:
                return False, errors

            # TODO: Enviar email de notificación
            # TODO: Crear recordatorio 2 días antes

            return True, []

        except Exception as e:
            return False, [f"Error al notificar auditoría: {str(e)}"]
