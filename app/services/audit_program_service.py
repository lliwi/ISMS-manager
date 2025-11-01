"""
Servicio para Gestión de Programas de Auditoría
ISO 27001:2022 - Cláusula 9.2.2 (Programa de auditoría interna)
"""
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from app.models.audit import (
    AuditProgram, AuditRecord, AuditSchedule, ProgramStatus,
    AuditFrequency, AuditType, AuditStatus
)
from models import db, User
import json


class AuditProgramService:
    """Servicio para gestión de programas anuales de auditoría"""

    @staticmethod
    def create_program(data, created_by_id):
        """
        Crea un nuevo programa de auditoría

        Args:
            data: Diccionario con datos del programa
            created_by_id: ID del usuario que crea el programa

        Returns:
            tuple: (program, errors)
        """
        errors = AuditProgramService.validate_create(data)
        if errors:
            return None, errors

        try:
            program = AuditProgram(
                year=data['year'],
                title=data['title'],
                description=data.get('description'),
                scope=data.get('scope'),
                objectives=data.get('objectives'),
                checklist_data=data.get('checklist_data'),
                start_date=data['start_date'],
                end_date=data['end_date'],
                status=ProgramStatus.DRAFT,
                created_by_id=created_by_id
            )

            db.session.add(program)
            db.session.commit()

            return program, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al crear programa: {str(e)}"]

    @staticmethod
    def validate_create(data):
        """Valida datos para crear programa"""
        errors = []

        # Campos obligatorios
        required_fields = ['year', 'title', 'start_date', 'end_date']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"El campo '{field}' es obligatorio")

        # Validar año
        if data.get('year'):
            year = int(data['year'])
            current_year = datetime.now().year

            if year < current_year:
                errors.append("No se pueden crear programas para años pasados")

            if year > current_year + 1:
                errors.append("Solo se pueden crear programas para el año actual y siguiente")

            # Verificar que no exista otro programa activo para el mismo año
            existing = AuditProgram.query.filter(
                AuditProgram.year == year,
                AuditProgram.status.in_([ProgramStatus.APPROVED, ProgramStatus.IN_PROGRESS])
            ).first()

            if existing:
                errors.append(f"Ya existe un programa activo para el año {year}")

        # Validar fechas
        if data.get('start_date') and data.get('end_date'):
            start = data['start_date']
            end = data['end_date']

            if isinstance(start, str):
                start = datetime.strptime(start, '%Y-%m-%d').date()
            if isinstance(end, str):
                end = datetime.strptime(end, '%Y-%m-%d').date()

            if start >= end:
                errors.append("La fecha de inicio debe ser anterior a la fecha de fin")

            # Las fechas deben estar dentro del año del programa
            if data.get('year'):
                year = int(data['year'])
                if start.year != year or end.year != year:
                    errors.append(f"Las fechas deben estar dentro del año {year}")

        return errors

    @staticmethod
    def update_program(program_id, data, updated_by_id):
        """Actualiza un programa existente"""
        program = AuditProgram.query.get(program_id)
        if not program:
            return None, ["Programa no encontrado"]

        # No permitir editar programas aprobados
        if program.status == ProgramStatus.APPROVED:
            return None, ["No se pueden editar programas aprobados"]

        try:
            if 'title' in data:
                program.title = data['title']
            if 'description' in data:
                program.description = data['description']
            if 'scope' in data:
                program.scope = data['scope']
            if 'objectives' in data:
                program.objectives = data['objectives']
            if 'checklist_data' in data:
                program.checklist_data = data['checklist_data']
            if 'start_date' in data:
                program.start_date = data['start_date']
            if 'end_date' in data:
                program.end_date = data['end_date']

            program.updated_at = datetime.utcnow()

            db.session.commit()
            return program, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al actualizar programa: {str(e)}"]

    @staticmethod
    def approve_program(program_id, approved_by_id):
        """Aprueba un programa de auditoría"""
        program = AuditProgram.query.get(program_id)
        if not program:
            return False, ["Programa no encontrado"]

        # Validar que puede aprobarse
        errors = AuditProgramService.validate_approval(program, approved_by_id)
        if errors:
            return False, errors

        try:
            program.status = ProgramStatus.APPROVED
            program.approved_by_id = approved_by_id
            program.approval_date = datetime.now().date()
            program.updated_at = datetime.utcnow()

            db.session.commit()

            # TODO: Notificar aprobación a auditores
            # TODO: Publicar en dashboard

            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al aprobar programa: {str(e)}"]

    @staticmethod
    def validate_approval(program, approver_id):
        """Valida que un programa puede aprobarse"""
        errors = []

        # Debe estar en borrador
        if program.status != ProgramStatus.DRAFT:
            errors.append("Solo se pueden aprobar programas en estado Borrador")

        # Verificar permisos del aprobador (debe ser CISO o Admin)
        approver = User.query.get(approver_id)
        if not approver:
            errors.append("Usuario aprobador no encontrado")
        elif not approver.has_role(['CISO', 'ADMIN']):
            errors.append("No tiene permisos para aprobar programas (requiere rol CISO o Admin)")

        # Debe tener auditorías planificadas
        if program.audits.count() == 0:
            errors.append("El programa no tiene auditorías planificadas")

        # Calcular cobertura ISO 27001
        coverage = AuditProgramService.calculate_iso27001_coverage(program.id)
        if coverage < 80:
            errors.append(
                f"Cobertura insuficiente ({coverage}%). Mínimo requerido: 80% de controles aplicables"
            )

        return errors

    @staticmethod
    def calculate_iso27001_coverage(program_id):
        """
        Calcula el porcentaje de cobertura de controles ISO 27001

        Returns:
            float: Porcentaje de cobertura (0-100)
        """
        program = AuditProgram.query.get(program_id)
        if not program:
            return 0

        # TODO: Obtener controles aplicables del SOA
        # Por ahora asumimos todos los controles del Anexo A (93 controles)
        total_applicable_controls = 93

        # Obtener controles auditados en el programa
        audited_controls = set()

        for audit in program.audits:
            if audit.audited_controls:
                try:
                    controls = json.loads(audit.audited_controls) if isinstance(
                        audit.audited_controls, str
                    ) else audit.audited_controls
                    audited_controls.update(controls)
                except:
                    pass

        if total_applicable_controls == 0:
            return 100

        coverage = (len(audited_controls) / total_applicable_controls) * 100
        return round(coverage, 2)

    @staticmethod
    def generate_annual_schedule(program_id, base_on_risks=True):
        """
        Genera propuesta de calendario de auditorías para el año

        Args:
            program_id: ID del programa
            base_on_risks: Si True, prioriza áreas de alto riesgo

        Returns:
            list: Lista de propuestas de auditorías
        """
        program = AuditProgram.query.get(program_id)
        if not program:
            return []

        # Definir áreas a auditar
        areas_to_audit = [
            {'area': 'Seguridad Física', 'controls': ['7.1', '7.2', '7.3'], 'priority': 'high'},
            {'area': 'Control de Acceso', 'controls': ['5.15', '5.16', '5.17', '5.18'], 'priority': 'high'},
            {'area': 'Criptografía', 'controls': ['8.24'], 'priority': 'medium'},
            {'area': 'Seguridad de Operaciones', 'controls': ['8.1', '8.6', '8.7'], 'priority': 'high'},
            {'area': 'Seguridad de Redes', 'controls': ['8.20', '8.21', '8.22'], 'priority': 'high'},
            {'area': 'Gestión de Incidentes', 'controls': ['5.24', '5.25', '5.26'], 'priority': 'medium'},
            {'area': 'Continuidad del Negocio', 'controls': ['5.29', '5.30'], 'priority': 'high'},
            {'area': 'Cumplimiento Legal', 'controls': ['5.31', '5.32', '5.33', '5.34'], 'priority': 'medium'},
        ]

        # Calcular frecuencia según prioridad
        frequency_map = {
            'high': AuditFrequency.SEMIANNUAL,
            'medium': AuditFrequency.ANNUAL,
            'low': AuditFrequency.ANNUAL
        }

        proposals = []
        start_date = program.start_date
        months_per_audit = 12 // len(areas_to_audit)

        for i, area_info in enumerate(areas_to_audit):
            # Calcular fecha propuesta
            audit_month = start_date.month + (i * months_per_audit)
            audit_year = start_date.year

            if audit_month > 12:
                audit_month -= 12
                audit_year += 1

            proposed_date = datetime(audit_year, audit_month, 15).date()

            frequency = frequency_map.get(area_info['priority'], AuditFrequency.ANNUAL)

            proposals.append({
                'area': area_info['area'],
                'controls': area_info['controls'],
                'priority': area_info['priority'],
                'frequency': frequency,
                'proposed_date': proposed_date,
                'estimated_duration_hours': 16 if area_info['priority'] == 'high' else 8
            })

        return proposals

    @staticmethod
    def add_schedule_item(program_id, data):
        """Agrega un item al cronograma del programa"""
        program = AuditProgram.query.get(program_id)
        if not program:
            return None, ["Programa no encontrado"]

        try:
            schedule = AuditSchedule(
                audit_program_id=program_id,
                area=data['area'],
                process=data.get('process'),
                frequency=AuditFrequency[data['frequency']],
                next_planned_date=data.get('next_planned_date'),
                priority=data.get('priority', 'medium'),
                estimated_duration_hours=data.get('estimated_duration_hours', 8)
            )

            db.session.add(schedule)
            db.session.commit()

            return schedule, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al agregar item al cronograma: {str(e)}"]

    @staticmethod
    def create_audit_from_schedule(schedule_id, created_by_id):
        """Crea una auditoría a partir de un item del cronograma"""
        schedule = AuditSchedule.query.get(schedule_id)
        if not schedule:
            return None, ["Item de cronograma no encontrado"]

        try:
            from app.services.audit_service import AuditService

            audit_data = {
                'title': f"Auditoría {schedule.area}",
                'audit_type': 'INTERNAL_PLANNED',
                'scope': f"Auditoría de {schedule.area}",
                'objectives': f"Verificar implementación de controles en {schedule.area}",
                'planned_date': schedule.next_planned_date,
                'audited_areas': json.dumps([schedule.area]),
                'lead_auditor_id': created_by_id  # TODO: Asignar auditor disponible
            }

            audit, errors = AuditService.create_audit(
                audit_data,
                created_by_id,
                schedule.audit_program_id
            )

            if audit:
                # Actualizar cronograma
                schedule.last_audit_date = datetime.now().date()

                # Calcular próxima fecha según frecuencia
                if schedule.frequency == AuditFrequency.ANNUAL:
                    schedule.next_planned_date = schedule.next_planned_date + timedelta(days=365)
                elif schedule.frequency == AuditFrequency.SEMIANNUAL:
                    schedule.next_planned_date = schedule.next_planned_date + timedelta(days=182)
                elif schedule.frequency == AuditFrequency.QUARTERLY:
                    schedule.next_planned_date = schedule.next_planned_date + timedelta(days=91)

                db.session.commit()

            return audit, errors

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al crear auditoría: {str(e)}"]

    @staticmethod
    def get_program_metrics(program_id):
        """Obtiene métricas del programa de auditoría"""
        program = AuditProgram.query.get(program_id)
        if not program:
            return None

        audits = program.audits.all()
        total_audits = len(audits)

        completed = len([a for a in audits if a.status in [
            AuditStatus.COMPLETED, AuditStatus.CLOSED
        ]])

        in_progress = len([a for a in audits if a.status == AuditStatus.IN_PROGRESS])

        cancelled = len([a for a in audits if a.status == AuditStatus.CANCELLED])

        # Hallazgos totales
        from app.models.audit import FindingType
        total_findings = sum(a.total_findings for a in audits)
        major_ncs = sum(a.major_findings_count for a in audits)
        minor_ncs = sum(a.minor_findings_count for a in audits)

        # Cobertura ISO 27001
        coverage = AuditProgramService.calculate_iso27001_coverage(program_id)

        return {
            'program_id': program_id,
            'year': program.year,
            'status': program.status.value,
            'total_audits': total_audits,
            'completed_audits': completed,
            'in_progress_audits': in_progress,
            'cancelled_audits': cancelled,
            'completion_rate': round((completed / total_audits * 100) if total_audits > 0 else 0, 2),
            'iso27001_coverage': coverage,
            'total_findings': total_findings,
            'major_ncs': major_ncs,
            'minor_ncs': minor_ncs,
            'average_findings_per_audit': round(
                total_findings / completed, 2
            ) if completed > 0 else 0
        }

    @staticmethod
    def get_programs_list(filters=None, page=1, per_page=20):
        """Obtiene lista de programas con filtros"""
        query = AuditProgram.query

        if filters:
            if filters.get('year'):
                query = query.filter(AuditProgram.year == filters['year'])

            if filters.get('status'):
                query = query.filter(AuditProgram.status == filters['status'])

        # Ordenar por año descendente
        query = query.order_by(AuditProgram.year.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_current_program():
        """Obtiene el programa del año actual"""
        current_year = datetime.now().year

        return AuditProgram.query.filter(
            AuditProgram.year == current_year,
            AuditProgram.status.in_([ProgramStatus.APPROVED, ProgramStatus.IN_PROGRESS])
        ).first()

    @staticmethod
    def propose_program_from_previous_year(year):
        """
        Genera propuesta de programa basado en el año anterior

        Args:
            year: Año para el nuevo programa

        Returns:
            dict: Propuesta de programa
        """
        previous_year = year - 1
        previous_program = AuditProgram.query.filter_by(year=previous_year).first()

        if not previous_program:
            return None

        # Analizar programa anterior
        previous_audits = previous_program.audits.all()

        # Identificar áreas con hallazgos
        areas_with_findings = {}
        for audit in previous_audits:
            if audit.total_findings > 0:
                area = audit.audited_areas or audit.title
                areas_with_findings[area] = audit.total_findings

        # Proponer auditorías
        proposals = []

        # Mantener auditorías del año anterior
        for audit in previous_audits:
            # Aumentar frecuencia si hubo hallazgos
            frequency = AuditFrequency.ANNUAL
            if audit.total_findings > 5:
                frequency = AuditFrequency.SEMIANNUAL

            proposals.append({
                'area': audit.audited_areas or audit.title,
                'controls': audit.audited_controls,
                'frequency': frequency,
                'priority': 'high' if audit.major_findings_count > 0 else 'medium',
                'reason': f"Continuidad del programa anterior. Hallazgos previos: {audit.total_findings}"
            })

        return {
            'year': year,
            'title': f"Programa de Auditorías Internas {year}",
            'description': f"Programa anual basado en resultados de {previous_year}",
            'proposed_audits': proposals,
            'areas_with_findings': areas_with_findings,
            'recommendations': [
                f"Priorizar auditorías en áreas con hallazgos críticos del año anterior",
                f"Aumentar frecuencia en controles con no conformidades mayores",
                f"Considerar incluir auditorías de seguimiento en Q1"
            ]
        }

    @staticmethod
    def close_program(program_id, closed_by_id):
        """Cierra un programa completado"""
        program = AuditProgram.query.get(program_id)
        if not program:
            return False, ["Programa no encontrado"]

        # Verificar que todas las auditorías estén cerradas
        open_audits = program.audits.filter(
            AuditRecord.status.in_([
                AuditStatus.PLANNED,
                AuditStatus.NOTIFIED,
                AuditStatus.PREPARATION,
                AuditStatus.IN_PROGRESS,
                AuditStatus.REPORTING,
                AuditStatus.COMPLETED
            ])
        ).count()

        if open_audits > 0:
            return False, [f"Hay {open_audits} auditorías pendientes de cierre"]

        try:
            program.status = ProgramStatus.COMPLETED
            program.updated_at = datetime.utcnow()

            db.session.commit()

            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al cerrar programa: {str(e)}"]

    @staticmethod
    def get_calendar_events(program_id):
        """Obtiene eventos del programa para calendario"""
        program = AuditProgram.query.get(program_id)
        if not program:
            return []

        events = []

        for audit in program.audits:
            color = 'blue'
            if audit.status == AuditStatus.COMPLETED:
                color = 'green'
            elif audit.status == AuditStatus.CANCELLED:
                color = 'red'
            elif audit.status == AuditStatus.IN_PROGRESS:
                color = 'orange'

            event = {
                'id': audit.id,
                'title': audit.title,
                'start': audit.planned_date.isoformat() if audit.planned_date else None,
                'end': audit.end_date.isoformat() if audit.end_date else None,
                'color': color,
                'url': f'/auditorias/{audit.id}',
                'extendedProps': {
                    'audit_code': audit.audit_code,
                    'status': audit.status.value,
                    'lead_auditor': audit.lead_auditor.full_name if audit.lead_auditor else None,
                    'findings': audit.total_findings
                }
            }

            events.append(event)

        return events
