"""
Servicio para Gestión de Acciones Correctivas
ISO 27001:2022 - Cláusula 10.2 (No conformidad y acciones correctivas)
"""
from datetime import datetime, timedelta
from sqlalchemy import or_
from app.models.audit import (
    AuditCorrectiveAction, AuditFinding, ActionType, ActionStatus
)
from models import db, User


class CorrectiveActionService:
    """Servicio para gestión de acciones correctivas"""

    @staticmethod
    def create_action(finding_id, data, created_by_id):
        """
        Crea una nueva acción correctiva

        Args:
            finding_id: ID del hallazgo
            data: Diccionario con datos de la acción
            created_by_id: ID del usuario que crea la acción

        Returns:
            tuple: (action, errors)
        """
        errors = CorrectiveActionService.validate_create(finding_id, data)
        if errors:
            return None, errors

        finding = AuditFinding.query.get(finding_id)
        if not finding:
            return None, ["Hallazgo no encontrado"]

        try:
            # Generar código único
            action_code = AuditCorrectiveAction.generate_action_code()

            # Procesar campos numéricos (convertir cadenas vacías a None)
            estimated_cost = data.get('estimated_cost')
            if estimated_cost == '' or estimated_cost is None:
                estimated_cost = None
            else:
                try:
                    estimated_cost = float(estimated_cost)
                except (ValueError, TypeError):
                    estimated_cost = None

            # Crear acción
            action = AuditCorrectiveAction(
                action_code=action_code,
                finding_id=finding_id,
                action_type=ActionType[data['action_type']],
                description=data['description'],
                implementation_plan=data.get('implementation_plan'),
                responsible_id=data['responsible_id'],
                verifier_id=data.get('verifier_id'),
                planned_start_date=data.get('planned_start_date'),
                planned_completion_date=data['planned_completion_date'],
                status=ActionStatus.PLANNED,
                estimated_cost=estimated_cost,
                resources_needed=data.get('resources_required') or None,  # Convertir cadena vacía a None
                priority=data.get('priority'),
                expected_benefit=data.get('expected_benefit') or None,
                success_criteria=data.get('success_criteria') or None,
                notes=data.get('notes') or None,
                progress_percentage=0
            )

            db.session.add(action)
            db.session.commit()

            # Actualizar estado del hallazgo
            from app.services.finding_service import FindingService
            from app.models.audit import FindingStatus

            if finding.status == FindingStatus.OPEN:
                FindingService.change_status(
                    finding_id,
                    FindingStatus.ACTION_PLAN_PENDING,
                    created_by_id
                )

            # TODO: Notificar al responsable
            # TODO: Crear recordatorio de seguimiento

            return action, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al crear acción correctiva: {str(e)}"]

    @staticmethod
    def validate_create(finding_id, data):
        """Valida datos para crear acción correctiva"""
        errors = []

        # Campos obligatorios
        required_fields = ['action_type', 'description', 'responsible_id', 'planned_completion_date']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"El campo '{field}' es obligatorio")

        # Validar tipo de acción
        if data.get('action_type'):
            try:
                ActionType[data['action_type']]
            except KeyError:
                errors.append("Tipo de acción no válido")

        # Validar responsable
        if data.get('responsible_id'):
            responsible = User.query.get(data['responsible_id'])
            if not responsible:
                errors.append("Responsable no encontrado")

        # Validar verificador
        if data.get('verifier_id'):
            verifier = User.query.get(data['verifier_id'])
            if not verifier:
                errors.append("Verificador no encontrado")

            # Verificador debe ser diferente al responsable
            if data.get('responsible_id') == data.get('verifier_id'):
                errors.append("El verificador debe ser diferente al responsable")

        # Validar fechas
        if data.get('planned_completion_date'):
            completion_date = data['planned_completion_date']

            # No puede ser en el pasado
            if isinstance(completion_date, str):
                completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()

            if completion_date < datetime.now().date():
                errors.append("La fecha de finalización no puede ser en el pasado")

            # No puede ser más de 1 año en el futuro
            max_date = datetime.now().date() + timedelta(days=365)
            if completion_date > max_date:
                errors.append("La fecha de finalización es demasiado lejana (máx. 1 año)")

        return errors

    @staticmethod
    def update_action(action_id, data, updated_by_id):
        """Actualiza una acción correctiva"""
        action = AuditCorrectiveAction.query.get(action_id)
        if not action:
            return None, ["Acción correctiva no encontrada"]

        # No permitir editar acciones completadas o verificadas
        if action.status in [ActionStatus.COMPLETED, ActionStatus.VERIFIED]:
            return None, ["No se pueden editar acciones completadas o verificadas"]

        try:
            # Actualizar campos
            if 'description' in data:
                action.description = data['description']
            if 'implementation_plan' in data:
                action.implementation_plan = data['implementation_plan']
            if 'responsible_id' in data:
                action.responsible_id = data['responsible_id']
            if 'verifier_id' in data:
                # Verificar que sea diferente al responsable
                if data['verifier_id'] == action.responsible_id:
                    return None, ["El verificador debe ser diferente al responsable"]
                action.verifier_id = data['verifier_id']
            if 'planned_completion_date' in data:
                action.planned_completion_date = data['planned_completion_date']
            if 'estimated_cost' in data:
                # Convertir cadena vacía a None
                estimated_cost = data['estimated_cost']
                if estimated_cost == '' or estimated_cost is None:
                    action.estimated_cost = None
                else:
                    try:
                        action.estimated_cost = float(estimated_cost)
                    except (ValueError, TypeError):
                        action.estimated_cost = None
            if 'resources_needed' in data:
                action.resources_needed = data['resources_needed'] or None

            action.updated_at = datetime.utcnow()

            db.session.commit()
            return action, []

        except Exception as e:
            db.session.rollback()
            return None, [f"Error al actualizar acción: {str(e)}"]

    @staticmethod
    def update_progress(action_id, progress_percentage, notes, updated_by_id):
        """Actualiza el progreso de una acción"""
        action = AuditCorrectiveAction.query.get(action_id)
        if not action:
            return False, ["Acción correctiva no encontrada"]

        if action.status not in [ActionStatus.PLANNED, ActionStatus.IN_PROGRESS]:
            return False, ["Solo se puede actualizar progreso de acciones planificadas o en progreso"]

        if not 0 <= progress_percentage <= 100:
            return False, ["El progreso debe estar entre 0 y 100"]

        try:
            action.progress_percentage = progress_percentage
            action.progress_notes = notes
            action.updated_at = datetime.utcnow()

            # Si el progreso > 0 y estado es PLANNED, cambiar a IN_PROGRESS
            if progress_percentage > 0 and action.status == ActionStatus.PLANNED:
                action.status = ActionStatus.IN_PROGRESS
                action.planned_start_date = datetime.now().date()

            db.session.commit()

            # TODO: Notificar actualización de progreso

            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al actualizar progreso: {str(e)}"]

    @staticmethod
    def complete_action(action_id, completed_by_id, completion_notes=None, actual_cost=None):
        """Marca una acción como completada"""
        action = AuditCorrectiveAction.query.get(action_id)
        if not action:
            return False, ["Acción correctiva no encontrada"]

        errors = CorrectiveActionService.validate_completion(action)
        if errors:
            return False, errors

        try:
            action.status = ActionStatus.COMPLETED
            action.progress_percentage = 100
            action.actual_completion_date = datetime.now().date()
            action.actual_cost = actual_cost
            if completion_notes:
                action.progress_notes = completion_notes
            action.updated_at = datetime.utcnow()

            db.session.commit()

            # Actualizar estado del hallazgo
            from app.services.finding_service import FindingService
            from app.models.audit import FindingStatus

            if action.finding.status == FindingStatus.IN_TREATMENT:
                # Verificar si todas las acciones están completadas
                all_completed = all(
                    a.status in [ActionStatus.COMPLETED, ActionStatus.VERIFIED]
                    for a in action.finding.corrective_actions
                )

                if all_completed:
                    FindingService.change_status(
                        action.finding_id,
                        FindingStatus.RESOLVED,
                        completed_by_id
                    )

            # TODO: Notificar al verificador
            # TODO: Crear tarea de verificación (3 meses después)

            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al completar acción: {str(e)}"]

    @staticmethod
    def validate_completion(action):
        """Valida que una acción puede completarse"""
        errors = []

        # Progreso debe ser 100%
        if action.progress_percentage < 100:
            errors.append("El progreso debe ser 100% para completar la acción")

        # Debe tener notas de implementación
        if not action.progress_notes:
            errors.append("Debe documentar la implementación de la acción")

        # Debe estar en progreso
        if action.status not in [ActionStatus.PLANNED, ActionStatus.IN_PROGRESS]:
            errors.append("Solo se pueden completar acciones planificadas o en progreso")

        return errors

    @staticmethod
    def verify_effectiveness(action_id, verifier_id, is_effective, verification_notes):
        """Verifica la eficacia de una acción completada"""
        action = AuditCorrectiveAction.query.get(action_id)
        if not action:
            return False, ["Acción correctiva no encontrada"]

        errors = CorrectiveActionService.validate_verification(action, verifier_id)
        if errors:
            return False, errors

        try:
            action.effectiveness_verified = is_effective
            action.effectiveness_notes = verification_notes
            action.effectiveness_verification_date = datetime.now().date()
            action.verification_date = datetime.now().date()

            if is_effective:
                action.status = ActionStatus.VERIFIED
            else:
                # Si no es efectiva, reabrir
                action.status = ActionStatus.IN_PROGRESS
                action.progress_percentage = 50  # Reducir progreso
                action.blocking_issues = f"Verificación fallida: {verification_notes}"

            action.updated_at = datetime.utcnow()

            db.session.commit()

            # Si la acción es efectiva, verificar estado del hallazgo
            if is_effective:
                from app.services.finding_service import FindingService
                from app.models.audit import FindingStatus

                # Verificar si todas las acciones están verificadas
                all_verified = all(
                    a.status == ActionStatus.VERIFIED
                    for a in action.finding.corrective_actions
                )

                if all_verified:
                    FindingService.change_status(
                        action.finding_id,
                        FindingStatus.VERIFIED,
                        verifier_id
                    )

            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al verificar eficacia: {str(e)}"]

    @staticmethod
    def validate_verification(action, verifier_id):
        """Valida que una acción puede verificarse"""
        errors = []

        # Acción debe estar completada
        if action.status != ActionStatus.COMPLETED:
            errors.append("Solo se pueden verificar acciones completadas")

        # Verificar que sea el verificador asignado
        if action.verifier_id != verifier_id:
            errors.append("No es el verificador asignado para esta acción")

        # Tiempo mínimo de implementación (3 meses)
        if action.actual_completion_date:
            min_date = action.actual_completion_date + timedelta(days=90)
            if datetime.now().date() < min_date:
                days_remaining = (min_date - datetime.now().date()).days
                errors.append(
                    f"Debe esperar {days_remaining} días más para verificar eficacia (mín. 3 meses)"
                )

        return errors

    @staticmethod
    def get_actions_list(filters=None, page=1, per_page=20):
        """Obtiene lista de acciones correctivas con filtros"""
        query = AuditCorrectiveAction.query

        if filters:
            if filters.get('finding_id'):
                query = query.filter(AuditCorrectiveAction.finding_id == filters['finding_id'])

            if filters.get('status'):
                query = query.filter(AuditCorrectiveAction.status == filters['status'])

            if filters.get('responsible_id'):
                query = query.filter(
                    AuditCorrectiveAction.responsible_id == filters['responsible_id']
                )

            if filters.get('verifier_id'):
                query = query.filter(AuditCorrectiveAction.verifier_id == filters['verifier_id'])

            if filters.get('overdue'):
                # Acciones vencidas
                query = query.filter(
                    AuditCorrectiveAction.status.in_([
                        ActionStatus.PLANNED,
                        ActionStatus.IN_PROGRESS
                    ]),
                    AuditCorrectiveAction.planned_completion_date < datetime.now().date()
                )

            if filters.get('pending_verification'):
                # Acciones completadas pendientes de verificación
                query = query.filter(
                    AuditCorrectiveAction.status == ActionStatus.COMPLETED,
                    AuditCorrectiveAction.actual_completion_date <=
                    datetime.now().date() - timedelta(days=90)
                )

        # Ordenar por fecha de creación descendente
        query = query.order_by(AuditCorrectiveAction.created_at.desc())

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_overdue_actions():
        """Obtiene acciones vencidas"""
        today = datetime.now().date()

        actions = AuditCorrectiveAction.query.filter(
            AuditCorrectiveAction.status.in_([
                ActionStatus.PLANNED,
                ActionStatus.IN_PROGRESS
            ]),
            AuditCorrectiveAction.planned_completion_date < today
        ).all()

        overdue = []
        for action in actions:
            days_overdue = (today - action.planned_completion_date).days
            overdue.append({
                'action': action,
                'days_overdue': days_overdue,
                'finding': action.finding,
                'responsible': action.responsible
            })

        return overdue

    @staticmethod
    def get_pending_verifications():
        """Obtiene acciones pendientes de verificación (completadas hace más de 3 meses)"""
        three_months_ago = datetime.now().date() - timedelta(days=90)

        actions = AuditCorrectiveAction.query.filter(
            AuditCorrectiveAction.status == ActionStatus.COMPLETED,
            AuditCorrectiveAction.actual_completion_date <= three_months_ago,
            AuditCorrectiveAction.effectiveness_verified == False
        ).all()

        return actions

    @staticmethod
    def get_action_summary(finding_id=None):
        """Obtiene resumen de acciones correctivas"""
        query = AuditCorrectiveAction.query

        if finding_id:
            query = query.filter_by(finding_id=finding_id)

        actions = query.all()

        return {
            'total': len(actions),
            'planned': len([a for a in actions if a.status == ActionStatus.PLANNED]),
            'in_progress': len([a for a in actions if a.status == ActionStatus.IN_PROGRESS]),
            'completed': len([a for a in actions if a.status == ActionStatus.COMPLETED]),
            'verified': len([a for a in actions if a.status == ActionStatus.VERIFIED]),
            'rejected': len([a for a in actions if a.status == ActionStatus.REJECTED]),
            'avg_progress': sum(a.progress_percentage for a in actions) / len(actions) if actions else 0,
            'overdue': len([a for a in actions if a.status in [ActionStatus.PLANNED, ActionStatus.IN_PROGRESS]
                           and a.planned_completion_date < datetime.now().date()])
        }

    @staticmethod
    def calculate_effectiveness_rate():
        """Calcula tasa de eficacia de acciones correctivas"""
        verified_actions = AuditCorrectiveAction.query.filter_by(
            status=ActionStatus.VERIFIED
        ).all()

        if not verified_actions:
            return 0

        effective = len([a for a in verified_actions if a.effectiveness_verified])

        return round((effective / len(verified_actions)) * 100, 2)

    @staticmethod
    def reopen_action(action_id, reopened_by_id, reason):
        """Reabre una acción rechazada o con verificación fallida"""
        action = AuditCorrectiveAction.query.get(action_id)
        if not action:
            return False, ["Acción correctiva no encontrada"]

        if action.status not in [ActionStatus.REJECTED, ActionStatus.COMPLETED]:
            return False, ["Solo se pueden reabrir acciones rechazadas o con verificación fallida"]

        if not reason:
            return False, ["Debe proporcionar una razón para reabrir la acción"]

        try:
            action.status = ActionStatus.IN_PROGRESS
            action.progress_percentage = 50
            action.blocking_issues = f"Reapertura: {reason}"
            action.updated_at = datetime.utcnow()

            db.session.commit()

            # TODO: Notificar reapertura al responsable

            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al reabrir acción: {str(e)}"]

    @staticmethod
    def cancel_action(action_id, cancelled_by_id, reason):
        """Cancela una acción correctiva"""
        action = AuditCorrectiveAction.query.get(action_id)
        if not action:
            return False, ["Acción correctiva no encontrada"]

        if action.status in [ActionStatus.COMPLETED, ActionStatus.VERIFIED]:
            return False, ["No se pueden cancelar acciones completadas o verificadas"]

        if not reason:
            return False, ["Debe proporcionar una razón para cancelar la acción"]

        try:
            action.status = ActionStatus.CANCELLED
            action.blocking_issues = f"Cancelación: {reason}"
            action.updated_at = datetime.utcnow()

            db.session.commit()

            return True, []

        except Exception as e:
            db.session.rollback()
            return False, [f"Error al cancelar acción: {str(e)}"]

    @staticmethod
    def get_actions_by_responsible(user_id, include_completed=False):
        """Obtiene acciones asignadas a un responsable"""
        query = AuditCorrectiveAction.query.filter_by(responsible_id=user_id)

        if not include_completed:
            query = query.filter(
                AuditCorrectiveAction.status.in_([
                    ActionStatus.PLANNED,
                    ActionStatus.IN_PROGRESS
                ])
            )

        return query.order_by(
            AuditCorrectiveAction.planned_completion_date.asc()
        ).all()

    @staticmethod
    def get_actions_pending_verification_by_verifier(user_id):
        """Obtiene acciones pendientes de verificación para un verificador"""
        three_months_ago = datetime.now().date() - timedelta(days=90)

        return AuditCorrectiveAction.query.filter(
            AuditCorrectiveAction.verifier_id == user_id,
            AuditCorrectiveAction.status == ActionStatus.COMPLETED,
            AuditCorrectiveAction.actual_completion_date <= three_months_ago
        ).order_by(
            AuditCorrectiveAction.actual_completion_date.asc()
        ).all()
