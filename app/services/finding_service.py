"""
Servicio para Gestión de Hallazgos de Auditoría
ISO 27001:2022 - Cláusula 10.2 (No conformidad y acciones correctivas)
"""
from datetime import datetime, timedelta
from sqlalchemy import or_
from app.models.audit import (
    AuditFinding, AuditRecord, FindingType, FindingStatus,
    AuditCorrectiveAction
)
from models import db, User
import json


class FindingService:
    """Servicio para gestión de hallazgos de auditoría"""

    # Plazos de cierre por tipo de hallazgo (en días)
    CLOSURE_DEADLINES = {
        FindingType.MAJOR_NC: 30,
        FindingType.MINOR_NC: 60,
        FindingType.OBSERVATION: 90,
        FindingType.OPPORTUNITY_IMPROVEMENT: 120
    }

    @staticmethod
    def create_finding(audit_id, data, created_by_id):
        """
        Crea un nuevo hallazgo de auditoría

        Args:
            audit_id: ID de la auditoría
            data: Diccionario con datos del hallazgo
            created_by_id: ID del usuario que crea el hallazgo

        Returns:
            tuple: (finding, errors)
        """
        errors = FindingService.validate_create(audit_id, data)
        if errors:
            return None, errors

        audit = AuditRecord.query.get(audit_id)
        if not audit:
            return None, ["Auditoría no encontrada"]

        try:
            # Generar código único
            finding_code = AuditFinding.generate_finding_code(audit.audit_code)

            # Crear hallazgo
            finding = AuditFinding(
                finding_code=finding_code,
                audit_id=audit_id,
                finding_type=FindingType[data['finding_type']],
                title=data['title'],
                description=data['description'],
                affected_control=data.get('affected_control'),
                affected_clause=data.get('affected_clause'),
                audit_criteria=data.get('audit_criteria'),
                department=data.get('department'),
                process=data.get('process'),
                responsible_id=data.get('responsible_id'),
                evidence=data['evidence'],
                evidence_files=data.get('evidence_files'),
                root_cause=data.get('root_cause'),
                risk_level=data.get('risk_level', 'medium'),
                potential_impact=data.get('potential_impact'),
                status=FindingStatus.OPEN,
                created_by_id=created_by_id
            )

            db.session.add(finding)
            db.session.commit()

            # Actualizar contadores en la auditoría
            audit.update_findings_count()
            db.session.commit()

            # TODO: Notificar al responsable
            # TODO: Crear tarea de seguimiento

            return finding, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al crear hallazgo: {str(e)}"]

    @staticmethod
    def validate_create(audit_id, data):
        """Valida datos para crear hallazgo"""
        errors = []

        # Campos obligatorios
        required_fields = ['finding_type', 'title', 'description', 'evidence']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"El campo '{field}' es obligatorio")

        # Validar tipo de hallazgo
        if data.get('finding_type'):
            try:
                finding_type = FindingType[data['finding_type']]

                # Causa raíz obligatoria para NCs
                if finding_type in [FindingType.MAJOR_NC, FindingType.MINOR_NC]:
                    if not data.get('root_cause'):
                        errors.append(
                            "El análisis de causa raíz es obligatorio para no conformidades"
                        )
            except KeyError:
                errors.append("Tipo de hallazgo no válido")

        # Validar responsable
        if data.get('responsible_id'):
            responsible = User.query.get(data['responsible_id'])
            if not responsible:
                errors.append("Responsable no encontrado")

        # Validar control ISO 27001
        if data.get('affected_control'):
            # TODO: Validar contra lista de controles del Anexo A
            pass

        return errors

    @staticmethod
    def update_finding(finding_id, data, updated_by_id):
        """Actualiza un hallazgo existente"""
        finding = AuditFinding.query.get(finding_id)
        if not finding:
            return None, ["Hallazgo no encontrado"]

        try:
            # Actualizar campos
            if 'title' in data:
                finding.title = data['title']
            if 'description' in data:
                finding.description = data['description']
            if 'evidence' in data:
                finding.evidence = data['evidence']
            if 'root_cause' in data:
                finding.root_cause = data['root_cause']
            if 'risk_level' in data:
                finding.risk_level = data['risk_level']
            if 'potential_impact' in data:
                finding.potential_impact = data['potential_impact']
            if 'affected_control' in data:
                finding.affected_control = data['affected_control']
            if 'affected_clause' in data:
                finding.affected_clause = data['affected_clause']
            if 'responsible_id' in data:
                finding.responsible_id = data['responsible_id']
            if 'department' in data:
                finding.department = data['department']

            finding.updated_at = datetime.utcnow()

            db.session.commit()
            return finding, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al actualizar hallazgo: {str(e)}"]

    @staticmethod
    def change_status(finding_id, new_status, user_id, notes=None):
        """Cambia el estado de un hallazgo"""
        finding = AuditFinding.query.get(finding_id)
        if not finding:
            return False, ["Hallazgo no encontrado"]

        # Validar transición
        errors = FindingService.validate_status_transition(finding, new_status)
        if errors:
            return False, errors

        try:
            old_status = finding.status
            finding.status = new_status
            finding.updated_at = datetime.utcnow()

            db.session.commit()

            # TODO: Registrar cambio en audit_log
            # TODO: Notificar cambio de estado

            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al cambiar estado: {str(e)}"]

    @staticmethod
    def validate_status_transition(finding, new_status):
        """Valida transición de estado del hallazgo"""
        errors = []

        # Transiciones permitidas
        allowed_transitions = {
            FindingStatus.OPEN: [
                FindingStatus.ACTION_PLAN_PENDING,
                FindingStatus.ACTION_PLAN_APPROVED
            ],
            FindingStatus.ACTION_PLAN_PENDING: [
                FindingStatus.ACTION_PLAN_APPROVED,
                FindingStatus.OPEN
            ],
            FindingStatus.ACTION_PLAN_APPROVED: [
                FindingStatus.IN_TREATMENT
            ],
            FindingStatus.IN_TREATMENT: [
                FindingStatus.RESOLVED
            ],
            FindingStatus.RESOLVED: [
                FindingStatus.VERIFIED,
                FindingStatus.IN_TREATMENT  # Reapertura
            ],
            FindingStatus.VERIFIED: [
                FindingStatus.CLOSED
            ],
            FindingStatus.CLOSED: [],
            FindingStatus.DEFERRED: [
                FindingStatus.OPEN
            ]
        }

        current_status = finding.status
        if new_status not in allowed_transitions.get(current_status, []):
            errors.append(
                f"Transición no permitida: {current_status.value} → {new_status.value}"
            )

        # Validaciones específicas
        if new_status == FindingStatus.ACTION_PLAN_APPROVED:
            if finding.corrective_actions.count() == 0:
                errors.append("Debe tener al menos un plan de acción")

        if new_status == FindingStatus.RESOLVED:
            from app.models.audit import AuditActionStatus
            completed_actions = finding.corrective_actions.filter_by(
                status=AuditActionStatus.COMPLETED
            ).count()
            if completed_actions == 0:
                errors.append("Debe tener al menos una acción completada")

        if new_status == FindingStatus.CLOSED:
            verified_actions = finding.corrective_actions.filter_by(
                effectiveness_verified=True
            ).count()
            if verified_actions == 0:
                errors.append("Las acciones deben estar verificadas")

        return errors

    @staticmethod
    def calculate_deadline(finding_type):
        """Calcula la fecha límite de cierre según el tipo de hallazgo"""
        days = FindingService.CLOSURE_DEADLINES.get(finding_type, 60)
        return datetime.now().date() + timedelta(days=days)

    @staticmethod
    def get_findings_list(filters=None, page=1, per_page=20):
        """
        Obtiene lista de hallazgos con filtros

        Args:
            filters: Diccionario con filtros
            page: Número de página
            per_page: Resultados por página

        Returns:
            Pagination object
        """
        query = AuditFinding.query

        if filters:
            if filters.get('audit_id'):
                query = query.filter(AuditFinding.audit_id == filters['audit_id'])

            if filters.get('finding_type'):
                query = query.filter(
                    AuditFinding.finding_type == filters['finding_type']
                )

            if filters.get('status'):
                query = query.filter(AuditFinding.status == filters['status'])

            if filters.get('responsible_id'):
                query = query.filter(
                    AuditFinding.responsible_id == filters['responsible_id']
                )

            if filters.get('risk_level'):
                query = query.filter(AuditFinding.risk_level == filters['risk_level'])

            if filters.get('affected_control'):
                query = query.filter(
                    AuditFinding.affected_control == filters['affected_control']
                )

            if filters.get('department'):
                query = query.filter(AuditFinding.department == filters['department'])

            if filters.get('overdue'):
                # Hallazgos vencidos
                query = query.filter(AuditFinding.status.in_([
                    FindingStatus.OPEN,
                    FindingStatus.ACTION_PLAN_APPROVED,
                    FindingStatus.IN_TREATMENT
                ]))
                # TODO: Implementar lógica de vencimiento

            if filters.get('search'):
                search = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        AuditFinding.finding_code.like(search),
                        AuditFinding.title.like(search),
                        AuditFinding.description.like(search)
                    )
                )

        # Ordenar por fecha de creación descendente
        query = query.order_by(AuditFinding.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_overdue_findings():
        """Obtiene hallazgos vencidos"""
        today = datetime.now().date()

        # Obtener hallazgos abiertos o en tratamiento
        findings = AuditFinding.query.filter(
            AuditFinding.status.in_([
                FindingStatus.OPEN,
                FindingStatus.ACTION_PLAN_APPROVED,
                FindingStatus.IN_TREATMENT
            ])
        ).all()

        overdue = []
        for finding in findings:
            deadline = FindingService.calculate_deadline(finding.finding_type)
            days_since_creation = (today - finding.created_at.date()).days

            if days_since_creation > FindingService.CLOSURE_DEADLINES.get(
                finding.finding_type, 60
            ):
                overdue.append({
                    'finding': finding,
                    'days_overdue': days_since_creation - FindingService.CLOSURE_DEADLINES.get(
                        finding.finding_type, 60
                    ),
                    'deadline': deadline
                })

        return overdue

    @staticmethod
    def get_findings_summary(audit_id=None):
        """Obtiene resumen de hallazgos"""
        query = AuditFinding.query

        if audit_id:
            query = query.filter_by(audit_id=audit_id)

        findings = query.all()

        return {
            'total': len(findings),
            'major_nc': len([f for f in findings if f.finding_type == FindingType.MAJOR_NC]),
            'minor_nc': len([f for f in findings if f.finding_type == FindingType.MINOR_NC]),
            'observations': len([f for f in findings if f.finding_type == FindingType.OBSERVATION]),
            'opportunities': len([f for f in findings if f.finding_type == FindingType.OPPORTUNITY_IMPROVEMENT]),
            'open': len([f for f in findings if f.status == FindingStatus.OPEN]),
            'in_treatment': len([f for f in findings if f.status == FindingStatus.IN_TREATMENT]),
            'closed': len([f for f in findings if f.status == FindingStatus.CLOSED])
        }

    @staticmethod
    def get_findings_by_control(control_id=None):
        """Obtiene hallazgos agrupados por control ISO 27001"""
        query = AuditFinding.query

        if control_id:
            query = query.filter_by(affected_control=control_id)

        findings = query.all()

        # Agrupar por control
        by_control = {}
        for finding in findings:
            control = finding.affected_control or 'Sin asignar'
            if control not in by_control:
                by_control[control] = []
            by_control[control].append(finding)

        return by_control

    @staticmethod
    def get_recurrence_analysis():
        """Analiza la recurrencia de hallazgos"""
        # Obtener todos los hallazgos de los últimos 2 años
        two_years_ago = datetime.now() - timedelta(days=730)
        findings = AuditFinding.query.filter(
            AuditFinding.created_at >= two_years_ago
        ).all()

        recurrent_findings = []

        for finding in findings:
            if finding.affected_control:
                # Buscar hallazgos anteriores en el mismo control
                previous = AuditFinding.query.filter(
                    AuditFinding.affected_control == finding.affected_control,
                    AuditFinding.created_at < finding.created_at,
                    AuditFinding.id != finding.id
                ).first()

                if previous:
                    recurrent_findings.append({
                        'finding': finding,
                        'previous_finding': previous,
                        'control': finding.affected_control,
                        'time_between': (finding.created_at - previous.created_at).days
                    })

        return {
            'total_findings': len(findings),
            'recurrent_findings': len(recurrent_findings),
            'recurrence_rate': round(
                (len(recurrent_findings) / len(findings) * 100) if findings else 0,
                2
            ),
            'details': recurrent_findings
        }

    @staticmethod
    def export_findings_matrix(filters=None):
        """Exporta matriz de hallazgos para Excel"""
        query = AuditFinding.query

        if filters:
            # Aplicar filtros similares a get_findings_list
            pass

        findings = query.all()

        matrix = []
        for finding in findings:
            matrix.append({
                'Código': finding.finding_code,
                'Auditoría': finding.audit.audit_code if finding.audit else '',
                'Tipo': finding.finding_type.value,
                'Título': finding.title,
                'Control ISO 27001': finding.affected_control or '',
                'Departamento': finding.department or '',
                'Responsable': finding.responsible.full_name if finding.responsible else '',
                'Nivel de Riesgo': finding.risk_level,
                'Estado': finding.status.value,
                'Fecha Creación': finding.created_at.strftime('%Y-%m-%d'),
                'Causa Raíz': finding.root_cause or '',
                'Acciones': finding.corrective_actions.count()
            })

        return matrix

    @staticmethod
    def close_finding(finding_id, closed_by_id, closure_notes=None):
        """Cierra un hallazgo después de verificación"""
        finding = AuditFinding.query.get(finding_id)
        if not finding:
            return False, ["Hallazgo no encontrado"]

        # Validar que puede cerrarse
        errors = FindingService.validate_closure(finding)
        if errors:
            return False, errors

        try:
            success, errors = FindingService.change_status(
                finding_id,
                FindingStatus.CLOSED,
                closed_by_id,
                closure_notes
            )

            if not success:
                return False, errors

            # Actualizar contadores de la auditoría
            finding.audit.update_findings_count()
            db.session.commit()

            return True, []

        except Exception as e:
            return False, [f"Error al cerrar hallazgo: {str(e)}"]

    @staticmethod
    def validate_closure(finding):
        """Valida que un hallazgo puede cerrarse"""
        errors = []

        # Debe estar en estado VERIFIED
        if finding.status != FindingStatus.VERIFIED:
            errors.append("Solo se pueden cerrar hallazgos verificados")

        # Todas las acciones deben estar completadas y verificadas
        for action in finding.corrective_actions:
            from app.models.audit import AuditActionStatus
            if action.status != AuditActionStatus.VERIFIED:
                errors.append(
                    f"Acción {action.action_code} no está verificada"
                )

            if not action.effectiveness_verified:
                errors.append(
                    f"Eficacia de acción {action.action_code} no verificada"
                )

        return errors

    @staticmethod
    def reopen_finding(finding_id, reopened_by_id, reason):
        """Reabre un hallazgo cerrado"""
        finding = AuditFinding.query.get(finding_id)
        if not finding:
            return False, ["Hallazgo no encontrado"]

        if finding.status not in [FindingStatus.VERIFIED, FindingStatus.CLOSED]:
            return False, ["Solo se pueden reabrir hallazgos verificados o cerrados"]

        if not reason:
            return False, ["Debe proporcionar una razón para reabrir el hallazgo"]

        try:
            success, errors = FindingService.change_status(
                finding_id,
                FindingStatus.IN_TREATMENT,
                reopened_by_id,
                f"Reapertura: {reason}"
            )

            if not success:
                return False, errors

            # TODO: Notificar reapertura

            return True, []

        except Exception as e:
            return False, [f"Error al reabrir hallazgo: {str(e)}"]
