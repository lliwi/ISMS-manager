"""
Servicio de workflow para gestión de cambios
Gestiona las transiciones de estado y validaciones
"""
from app.models.change import ChangeStatus, Change
from typing import Dict, List


class ChangeWorkflow:
    """Gestión del workflow de cambios"""

    # Definir transiciones válidas
    TRANSITIONS = {
        ChangeStatus.DRAFT: [ChangeStatus.SUBMITTED, ChangeStatus.CANCELLED],
        ChangeStatus.SUBMITTED: [ChangeStatus.UNDER_REVIEW, ChangeStatus.DRAFT, ChangeStatus.CANCELLED],
        ChangeStatus.UNDER_REVIEW: [ChangeStatus.PENDING_APPROVAL, ChangeStatus.SUBMITTED, ChangeStatus.REJECTED, ChangeStatus.CANCELLED],
        ChangeStatus.PENDING_APPROVAL: [ChangeStatus.APPROVED, ChangeStatus.REJECTED, ChangeStatus.UNDER_REVIEW],
        ChangeStatus.APPROVED: [ChangeStatus.SCHEDULED, ChangeStatus.CANCELLED],
        ChangeStatus.REJECTED: [ChangeStatus.DRAFT, ChangeStatus.CANCELLED],
        ChangeStatus.SCHEDULED: [ChangeStatus.IN_PROGRESS, ChangeStatus.APPROVED, ChangeStatus.CANCELLED],
        ChangeStatus.IN_PROGRESS: [ChangeStatus.IMPLEMENTED, ChangeStatus.FAILED, ChangeStatus.ROLLED_BACK],
        ChangeStatus.IMPLEMENTED: [ChangeStatus.UNDER_VALIDATION, ChangeStatus.ROLLED_BACK],
        ChangeStatus.UNDER_VALIDATION: [ChangeStatus.CLOSED, ChangeStatus.FAILED, ChangeStatus.ROLLED_BACK],
        ChangeStatus.CLOSED: [],  # Estado final
        ChangeStatus.CANCELLED: [],  # Estado final
        ChangeStatus.FAILED: [ChangeStatus.DRAFT, ChangeStatus.ROLLED_BACK],
        ChangeStatus.ROLLED_BACK: [ChangeStatus.DRAFT]
    }

    # Estados que requieren aprobación CAB
    CAB_REQUIRED_STATES = [ChangeStatus.PENDING_APPROVAL]

    # Estados que permiten edición
    EDITABLE_STATES = [
        ChangeStatus.DRAFT,
        ChangeStatus.SUBMITTED,
        ChangeStatus.UNDER_REVIEW
    ]

    # Estados finales (no permiten más cambios)
    FINAL_STATES = [
        ChangeStatus.CLOSED,
        ChangeStatus.CANCELLED
    ]

    @staticmethod
    def can_transition(current_status: ChangeStatus, new_status: ChangeStatus) -> bool:
        """
        Verifica si una transición de estado es válida

        Args:
            current_status: Estado actual
            new_status: Nuevo estado deseado

        Returns:
            True si la transición es válida
        """
        if current_status not in ChangeWorkflow.TRANSITIONS:
            return False

        return new_status in ChangeWorkflow.TRANSITIONS[current_status]

    @staticmethod
    def get_available_transitions(current_status: ChangeStatus) -> List[ChangeStatus]:
        """
        Obtiene las transiciones disponibles desde un estado

        Args:
            current_status: Estado actual

        Returns:
            Lista de estados a los que se puede transicionar
        """
        return ChangeWorkflow.TRANSITIONS.get(current_status, [])

    @staticmethod
    def is_editable(status: ChangeStatus) -> bool:
        """
        Verifica si un cambio es editable en su estado actual

        Args:
            status: Estado del cambio

        Returns:
            True si es editable
        """
        return status in ChangeWorkflow.EDITABLE_STATES

    @staticmethod
    def is_final(status: ChangeStatus) -> bool:
        """
        Verifica si un estado es final

        Args:
            status: Estado a verificar

        Returns:
            True si es estado final
        """
        return status in ChangeWorkflow.FINAL_STATES

    @staticmethod
    def requires_cab_approval(change: Change) -> bool:
        """
        Verifica si un cambio requiere aprobación del CAB

        Args:
            change: Objeto Change

        Returns:
            True si requiere aprobación CAB
        """
        from app.models.change import ChangeCategory

        # Los cambios MAJOR y EMERGENCY siempre requieren CAB
        if change.category in [ChangeCategory.MAJOR, ChangeCategory.EMERGENCY]:
            return True

        # Los cambios de alto riesgo requieren CAB
        from app.models.change import RiskLevel
        if change.risk_level == RiskLevel.HIGH or change.risk_level == RiskLevel.CRITICAL:
            return True

        # Los cambios que afectan producción requieren CAB
        if change.affects_production:
            return True

        return False

    @staticmethod
    def validate_transition_requirements(change: Change, new_status: ChangeStatus) -> Dict:
        """
        Valida que se cumplan los requisitos para una transición

        Args:
            change: Objeto Change
            new_status: Nuevo estado deseado

        Returns:
            Dict con 'valid' (bool) y 'errors' (list)
        """
        errors = []

        # Validaciones específicas por transición
        if new_status == ChangeStatus.SUBMITTED:
            # Validar campos obligatorios
            if not change.title or not change.title.strip():
                errors.append("El título es obligatorio")
            if not change.description or not change.description.strip():
                errors.append("La descripción es obligatoria")
            if not change.business_justification:
                errors.append("La justificación de negocio es obligatoria")
            if not change.implementation_plan:
                errors.append("El plan de implementación es obligatorio")
            if not change.rollback_plan:
                errors.append("El plan de retroceso es obligatorio")

        elif new_status == ChangeStatus.PENDING_APPROVAL:
            # Validar que tenga evaluación de riesgos
            if not change.risk_assessment:
                errors.append("Se requiere evaluación de riesgos")
            if not change.risk_assessments:
                errors.append("Se requiere al menos una evaluación de riesgo detallada")

        elif new_status == ChangeStatus.APPROVED:
            # Validar que todas las aprobaciones estén completas
            from app.models.change import ApprovalStatus
            pending = [a for a in change.approvals if a.status == ApprovalStatus.PENDING]
            if pending:
                errors.append(f"Hay {len(pending)} aprobaciones pendientes")

        elif new_status == ChangeStatus.SCHEDULED:
            # Validar que tenga fechas programadas
            if not change.scheduled_start_date:
                errors.append("Se requiere fecha de inicio programada")
            if not change.scheduled_end_date:
                errors.append("Se requiere fecha de fin programada")
            if change.scheduled_start_date and change.scheduled_end_date:
                if change.scheduled_end_date <= change.scheduled_start_date:
                    errors.append("La fecha de fin debe ser posterior a la de inicio")

        elif new_status == ChangeStatus.IN_PROGRESS:
            # Validar que tenga tareas definidas
            if not change.tasks:
                errors.append("Se requiere al menos una tarea de implementación")

        elif new_status == ChangeStatus.IMPLEMENTED:
            # Validar que todas las tareas críticas estén completadas
            from app.models.change import TaskStatus
            critical_pending = [
                t for t in change.tasks
                if t.is_critical and t.status != TaskStatus.COMPLETED
            ]
            if critical_pending:
                errors.append(f"Hay {len(critical_pending)} tareas críticas pendientes")

        elif new_status == ChangeStatus.CLOSED:
            # Validar que tenga revisión post-implementación
            if not change.reviews:
                errors.append("Se requiere revisión post-implementación (PIR)")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    @staticmethod
    def get_workflow_progress(change: Change) -> Dict:
        """
        Obtiene el progreso del cambio en el workflow

        Args:
            change: Objeto Change

        Returns:
            Dict con información de progreso
        """
        # Mapear estados a porcentajes de progreso
        progress_map = {
            ChangeStatus.DRAFT: 5,
            ChangeStatus.SUBMITTED: 10,
            ChangeStatus.UNDER_REVIEW: 20,
            ChangeStatus.PENDING_APPROVAL: 30,
            ChangeStatus.APPROVED: 40,
            ChangeStatus.SCHEDULED: 50,
            ChangeStatus.IN_PROGRESS: 70,
            ChangeStatus.IMPLEMENTED: 85,
            ChangeStatus.UNDER_VALIDATION: 95,
            ChangeStatus.CLOSED: 100,
            ChangeStatus.REJECTED: 0,
            ChangeStatus.CANCELLED: 0,
            ChangeStatus.FAILED: 0,
            ChangeStatus.ROLLED_BACK: 0
        }

        current_progress = progress_map.get(change.status, 0)

        # Calcular progreso de tareas si está en implementación
        if change.status == ChangeStatus.IN_PROGRESS and change.tasks:
            task_progress = change.completion_percentage
            # Ajustar progreso entre 50% y 70% basado en tareas
            current_progress = 50 + (task_progress * 0.2)

        return {
            'percentage': int(current_progress),
            'status': change.status.value,
            'is_complete': change.status == ChangeStatus.CLOSED,
            'is_failed': change.status in [ChangeStatus.REJECTED, ChangeStatus.CANCELLED, ChangeStatus.FAILED, ChangeStatus.ROLLED_BACK]
        }

    @staticmethod
    def get_next_actions(change: Change) -> List[Dict]:
        """
        Obtiene las acciones siguientes disponibles para un cambio

        Args:
            change: Objeto Change

        Returns:
            Lista de acciones disponibles con metadata
        """
        actions = []

        # Mapear transiciones a acciones con metadata
        action_metadata = {
            ChangeStatus.SUBMITTED: {
                'label': 'Enviar para revisión',
                'icon': 'send',
                'class': 'btn-primary',
                'permission': 'submit'
            },
            ChangeStatus.UNDER_REVIEW: {
                'label': 'Iniciar revisión',
                'icon': 'search',
                'class': 'btn-info',
                'permission': 'review'
            },
            ChangeStatus.PENDING_APPROVAL: {
                'label': 'Solicitar aprobaciones',
                'icon': 'check-circle',
                'class': 'btn-warning',
                'permission': 'request_approval'
            },
            ChangeStatus.APPROVED: {
                'label': 'Aprobar',
                'icon': 'thumbs-up',
                'class': 'btn-success',
                'permission': 'approve'
            },
            ChangeStatus.REJECTED: {
                'label': 'Rechazar',
                'icon': 'thumbs-down',
                'class': 'btn-danger',
                'permission': 'approve'
            },
            ChangeStatus.SCHEDULED: {
                'label': 'Programar',
                'icon': 'calendar',
                'class': 'btn-primary',
                'permission': 'schedule'
            },
            ChangeStatus.IN_PROGRESS: {
                'label': 'Iniciar implementación',
                'icon': 'play',
                'class': 'btn-success',
                'permission': 'implement'
            },
            ChangeStatus.IMPLEMENTED: {
                'label': 'Completar implementación',
                'icon': 'check',
                'class': 'btn-success',
                'permission': 'implement'
            },
            ChangeStatus.UNDER_VALIDATION: {
                'label': 'Iniciar validación',
                'icon': 'clipboard-check',
                'class': 'btn-info',
                'permission': 'validate'
            },
            ChangeStatus.CLOSED: {
                'label': 'Cerrar',
                'icon': 'lock',
                'class': 'btn-success',
                'permission': 'close'
            },
            ChangeStatus.CANCELLED: {
                'label': 'Cancelar',
                'icon': 'ban',
                'class': 'btn-secondary',
                'permission': 'cancel'
            },
            ChangeStatus.ROLLED_BACK: {
                'label': 'Revertir',
                'icon': 'undo',
                'class': 'btn-danger',
                'permission': 'rollback'
            }
        }

        available_transitions = ChangeWorkflow.get_available_transitions(change.status)

        for next_status in available_transitions:
            if next_status in action_metadata:
                action = action_metadata[next_status].copy()
                action['next_status'] = next_status.value

                # Validar requisitos
                validation = ChangeWorkflow.validate_transition_requirements(change, next_status)
                action['enabled'] = validation['valid']
                action['errors'] = validation['errors']

                actions.append(action)

        return actions

    @staticmethod
    def get_status_badge_class(status: ChangeStatus) -> str:
        """
        Obtiene la clase CSS del badge para un estado

        Args:
            status: Estado del cambio

        Returns:
            Clase CSS de Bootstrap
        """
        badge_map = {
            ChangeStatus.DRAFT: 'badge-secondary',
            ChangeStatus.SUBMITTED: 'badge-info',
            ChangeStatus.UNDER_REVIEW: 'badge-warning',
            ChangeStatus.PENDING_APPROVAL: 'badge-warning',
            ChangeStatus.APPROVED: 'badge-success',
            ChangeStatus.REJECTED: 'badge-danger',
            ChangeStatus.SCHEDULED: 'badge-primary',
            ChangeStatus.IN_PROGRESS: 'badge-info',
            ChangeStatus.IMPLEMENTED: 'badge-success',
            ChangeStatus.UNDER_VALIDATION: 'badge-warning',
            ChangeStatus.CLOSED: 'badge-dark',
            ChangeStatus.CANCELLED: 'badge-secondary',
            ChangeStatus.FAILED: 'badge-danger',
            ChangeStatus.ROLLED_BACK: 'badge-danger'
        }

        return badge_map.get(status, 'badge-secondary')
