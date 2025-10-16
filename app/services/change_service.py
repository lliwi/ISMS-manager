"""
Servicio para la gestión de cambios según ISO 27001:2023
Control 6.3 - Planificación de cambios
Control 8.32 - Gestión de cambios
"""
from models import db
from app.models.change import (
    Change, ChangeApproval, ChangeTask, ChangeDocument,
    ChangeHistory, ChangeReview, ChangeRiskAssessment, ChangeAsset,
    ChangeStatus, ApprovalStatus, ApprovalLevel, TaskStatus, RiskLevel
)
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import or_, and_


class ChangeService:
    """Servicio principal para gestión de cambios"""

    @staticmethod
    def create_change(data: Dict, current_user_id: int) -> Change:
        """
        Crea un nuevo cambio

        Args:
            data: Diccionario con los datos del cambio
            current_user_id: ID del usuario actual

        Returns:
            Objeto Change creado
        """
        change = Change(
            change_code=Change.generate_change_code(),
            title=data['title'],
            description=data['description'],
            change_type=data['change_type'],
            category=data.get('category', 'STANDARD'),
            priority=data.get('priority', 'MEDIUM'),
            business_justification=data['business_justification'],
            implementation_plan=data['implementation_plan'],
            rollback_plan=data['rollback_plan'],
            requester_id=current_user_id,
            owner_id=data.get('owner_id', current_user_id),
            status=ChangeStatus.DRAFT,
            created_by_id=current_user_id
        )

        # Campos opcionales
        optional_fields = [
            'expected_benefits', 'impact_if_not_implemented', 'risk_assessment',
            'risk_level', 'impact_analysis', 'test_plan', 'communication_plan',
            'estimated_duration', 'estimated_cost', 'downtime_required',
            'estimated_downtime_minutes', 'scheduled_start_date', 'scheduled_end_date',
            'impact_confidentiality', 'impact_integrity', 'impact_availability',
            'affects_development', 'affects_testing', 'affects_production',
            'affected_services', 'affected_controls', 'affected_users_count'
        ]

        for field in optional_fields:
            if field in data:
                setattr(change, field, data[field])

        db.session.add(change)
        db.session.commit()

        # Registrar en historial
        ChangeService._add_history(
            change.id,
            'STATUS',
            None,
            'DRAFT',
            current_user_id,
            'Cambio creado'
        )

        return change

    @staticmethod
    def update_change(change_id: int, data: Dict, current_user_id: int) -> Change:
        """
        Actualiza un cambio existente

        Args:
            change_id: ID del cambio
            data: Diccionario con los datos a actualizar
            current_user_id: ID del usuario actual

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        # Solo se puede editar si está en ciertos estados
        editable_statuses = [ChangeStatus.DRAFT, ChangeStatus.SUBMITTED, ChangeStatus.UNDER_REVIEW]
        if change.status not in editable_statuses:
            raise ValueError(f"No se puede editar un cambio en estado {change.status.value}")

        # Registrar cambios en historial
        tracked_fields = {
            'title': 'Título',
            'description': 'Descripción',
            'change_type': 'Tipo',
            'category': 'Categoría',
            'priority': 'Prioridad',
            'risk_level': 'Nivel de riesgo',
            'scheduled_start_date': 'Fecha inicio programada',
            'scheduled_end_date': 'Fecha fin programada',
            'owner_id': 'Responsable'
        }

        for field, label in tracked_fields.items():
            if field in data:
                old_value = getattr(change, field)
                new_value = data[field]

                if old_value != new_value:
                    ChangeService._add_history(
                        change.id,
                        field,
                        str(old_value) if old_value else None,
                        str(new_value) if new_value else None,
                        current_user_id,
                        f'{label} modificado'
                    )
                    setattr(change, field, new_value)

        change.updated_at = datetime.utcnow()
        change.updated_by_id = current_user_id

        db.session.commit()
        return change

    @staticmethod
    def submit_for_review(change_id: int, current_user_id: int) -> Change:
        """
        Envía el cambio para revisión

        Args:
            change_id: ID del cambio
            current_user_id: ID del usuario actual

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        if change.status != ChangeStatus.DRAFT:
            raise ValueError("Solo se pueden enviar cambios en estado borrador")

        # Validar que tenga la información mínima requerida
        required_fields = [
            'title', 'description', 'business_justification',
            'implementation_plan', 'rollback_plan'
        ]

        for field in required_fields:
            if not getattr(change, field):
                raise ValueError(f"Campo requerido faltante: {field}")

        change.status = ChangeStatus.SUBMITTED
        change.updated_at = datetime.utcnow()
        change.updated_by_id = current_user_id

        ChangeService._add_history(
            change.id,
            'STATUS',
            'DRAFT',
            'SUBMITTED',
            current_user_id,
            'Cambio enviado para revisión'
        )

        # Crear registros de aprobación según la categoría del cambio
        # Para simplificar, creamos una aprobación técnica por defecto
        # TODO: Determinar niveles de aprobación según categoría (MINOR, STANDARD, MAJOR, EMERGENCY)
        approval = ChangeApproval(
            change_id=change.id,
            approval_level=ApprovalLevel.TECHNICAL,
            approver_id=current_user_id,  # TODO: Asignar al aprobador correcto según rol
            status=ApprovalStatus.PENDING
        )
        db.session.add(approval)

        db.session.commit()

        # TODO: Enviar notificaciones a revisores

        return change

    @staticmethod
    def request_approval(change_id: int, approvers: List[Dict], current_user_id: int) -> Change:
        """
        Solicita aprobaciones para el cambio

        Args:
            change_id: ID del cambio
            approvers: Lista de aprobadores con nivel y usuario
            current_user_id: ID del usuario actual

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        if change.status != ChangeStatus.UNDER_REVIEW:
            raise ValueError("El cambio debe estar en revisión para solicitar aprobaciones")

        # Crear registros de aprobación
        for approver_data in approvers:
            approval = ChangeApproval(
                change_id=change.id,
                approval_level=approver_data['level'],
                approver_id=approver_data['user_id'],
                status=ApprovalStatus.PENDING
            )
            db.session.add(approval)

        change.status = ChangeStatus.PENDING_APPROVAL
        change.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change.id,
            'STATUS',
            'UNDER_REVIEW',
            'PENDING_APPROVAL',
            current_user_id,
            'Aprobaciones solicitadas'
        )

        db.session.commit()

        # TODO: Enviar notificaciones a aprobadores

        return change

    @staticmethod
    def approve(change_id: int, approver_id: int, comments: str = None, conditions: str = None) -> ChangeApproval:
        """
        Aprueba un cambio

        Args:
            change_id: ID del cambio
            approver_id: ID del aprobador
            comments: Comentarios de la aprobación
            conditions: Condiciones de la aprobación

        Returns:
            Objeto ChangeApproval actualizado
        """
        # Buscar una aprobación pendiente para este cambio
        # TODO: Implementar lógica de permisos para verificar que el usuario puede aprobar
        approval = ChangeApproval.query.filter_by(
            change_id=change_id,
            status=ApprovalStatus.PENDING
        ).first()

        if not approval:
            raise ValueError("No hay aprobaciones pendientes para este cambio")

        # Actualizar el aprobador (en fase de testing, cualquier usuario puede aprobar)
        approval.approver_id = approver_id
        approval.status = ApprovalStatus.APPROVED
        approval.comments = comments
        approval.conditions = conditions
        approval.approved_date = datetime.utcnow()
        approval.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change_id,
            'APPROVAL',
            'PENDING',
            'APPROVED',
            approver_id,
            f'Aprobación {approval.approval_level.value} concedida'
        )

        # Verificar si todas las aprobaciones están completas
        change = Change.query.get(change_id)
        all_approved = all(a.status == ApprovalStatus.APPROVED for a in change.approvals)

        if all_approved:
            change.status = ChangeStatus.APPROVED
            ChangeService._add_history(
                change_id,
                'STATUS',
                'PENDING_APPROVAL',
                'APPROVED',
                approver_id,
                'Todas las aprobaciones completadas'
            )

        db.session.commit()

        # TODO: Enviar notificación

        return approval

    @staticmethod
    def reject(change_id: int, approver_id: int, comments: str) -> ChangeApproval:
        """
        Rechaza un cambio

        Args:
            change_id: ID del cambio
            approver_id: ID del aprobador
            comments: Comentarios del rechazo

        Returns:
            Objeto ChangeApproval actualizado
        """
        approval = ChangeApproval.query.filter_by(
            change_id=change_id,
            approver_id=approver_id,
            status=ApprovalStatus.PENDING
        ).first_or_404()

        approval.status = ApprovalStatus.REJECTED
        approval.comments = comments
        approval.approved_date = datetime.utcnow()
        approval.updated_at = datetime.utcnow()

        # Cambiar estado del cambio a rechazado
        change = Change.query.get(change_id)
        change.status = ChangeStatus.REJECTED
        change.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change_id,
            'STATUS',
            'PENDING_APPROVAL',
            'REJECTED',
            approver_id,
            f'Cambio rechazado: {comments}'
        )

        db.session.commit()

        # TODO: Enviar notificación al solicitante

        return approval

    @staticmethod
    def schedule(change_id: int, start_date: datetime, end_date: datetime, current_user_id: int) -> Change:
        """
        Programa la implementación del cambio

        Args:
            change_id: ID del cambio
            start_date: Fecha de inicio
            end_date: Fecha de fin
            current_user_id: ID del usuario actual

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        if change.status != ChangeStatus.APPROVED:
            raise ValueError("Solo se pueden programar cambios aprobados")

        change.scheduled_start_date = start_date
        change.scheduled_end_date = end_date
        change.status = ChangeStatus.SCHEDULED
        change.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change.id,
            'STATUS',
            'APPROVED',
            'SCHEDULED',
            current_user_id,
            f'Cambio programado para {start_date.strftime("%Y-%m-%d %H:%M")}'
        )

        db.session.commit()

        # TODO: Añadir al calendario
        # TODO: Enviar notificaciones

        return change

    @staticmethod
    def start_implementation(change_id: int, current_user_id: int) -> Change:
        """
        Inicia la implementación del cambio

        Args:
            change_id: ID del cambio
            current_user_id: ID del usuario actual

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        if change.status != ChangeStatus.SCHEDULED:
            raise ValueError("Solo se pueden implementar cambios programados")

        change.status = ChangeStatus.IN_PROGRESS
        change.actual_start_date = datetime.utcnow()
        change.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change.id,
            'STATUS',
            'SCHEDULED',
            'IN_PROGRESS',
            current_user_id,
            'Implementación iniciada'
        )

        db.session.commit()

        return change

    @staticmethod
    def complete_implementation(change_id: int, current_user_id: int, notes: str = None) -> Change:
        """
        Completa la implementación del cambio

        Args:
            change_id: ID del cambio
            current_user_id: ID del usuario actual
            notes: Notas de implementación

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        if change.status != ChangeStatus.IN_PROGRESS:
            raise ValueError("Solo se pueden completar cambios en progreso")

        change.status = ChangeStatus.IMPLEMENTED
        change.actual_end_date = datetime.utcnow()
        change.implementation_notes = notes

        # Calcular duración real
        if change.actual_start_date:
            delta = change.actual_end_date - change.actual_start_date
            change.actual_duration = int(delta.total_seconds() / 3600)  # Horas

        change.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change.id,
            'STATUS',
            'IN_PROGRESS',
            'IMPLEMENTED',
            current_user_id,
            'Implementación completada'
        )

        db.session.commit()

        return change

    @staticmethod
    def validate(change_id: int, current_user_id: int) -> Change:
        """
        Inicia la validación del cambio

        Args:
            change_id: ID del cambio
            current_user_id: ID del usuario actual

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        if change.status != ChangeStatus.IMPLEMENTED:
            raise ValueError("Solo se pueden validar cambios implementados")

        change.status = ChangeStatus.UNDER_VALIDATION
        change.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change.id,
            'STATUS',
            'IMPLEMENTED',
            'UNDER_VALIDATION',
            current_user_id,
            'Validación iniciada'
        )

        db.session.commit()

        return change

    @staticmethod
    def close(change_id: int, current_user_id: int, success: bool = True) -> Change:
        """
        Cierra el cambio

        Args:
            change_id: ID del cambio
            current_user_id: ID del usuario actual
            success: Si fue exitoso

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        if change.status != ChangeStatus.UNDER_VALIDATION:
            raise ValueError("Solo se pueden cerrar cambios en validación")

        change.status = ChangeStatus.CLOSED
        change.success_status = 'exitoso' if success else 'fallido'
        change.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change.id,
            'STATUS',
            'UNDER_VALIDATION',
            'CLOSED',
            current_user_id,
            f'Cambio cerrado - {"Exitoso" if success else "Fallido"}'
        )

        db.session.commit()

        return change

    @staticmethod
    def rollback(change_id: int, current_user_id: int, reason: str) -> Change:
        """
        Revierte un cambio

        Args:
            change_id: ID del cambio
            current_user_id: ID del usuario actual
            reason: Razón del rollback

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        old_status = change.status
        change.status = ChangeStatus.ROLLED_BACK
        change.issues_encountered = reason
        change.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change.id,
            'STATUS',
            old_status.value,
            'ROLLED_BACK',
            current_user_id,
            f'Cambio revertido: {reason}'
        )

        db.session.commit()

        # TODO: Crear incidente automático si es necesario

        return change

    @staticmethod
    def cancel(change_id: int, current_user_id: int, reason: str) -> Change:
        """
        Cancela un cambio

        Args:
            change_id: ID del cambio
            current_user_id: ID del usuario actual
            reason: Razón de la cancelación

        Returns:
            Objeto Change actualizado
        """
        change = Change.query.get_or_404(change_id)

        # Solo se pueden cancelar cambios que no estén cerrados
        if change.status in [ChangeStatus.CLOSED, ChangeStatus.ROLLED_BACK]:
            raise ValueError("No se puede cancelar un cambio cerrado o revertido")

        old_status = change.status
        change.status = ChangeStatus.CANCELLED
        change.notes = f"Cancelado: {reason}"
        change.updated_at = datetime.utcnow()

        ChangeService._add_history(
            change.id,
            'STATUS',
            old_status.value,
            'CANCELLED',
            current_user_id,
            f'Cambio cancelado: {reason}'
        )

        db.session.commit()

        return change

    @staticmethod
    def add_task(change_id: int, task_data: Dict, current_user_id: int) -> ChangeTask:
        """
        Añade una tarea al cambio

        Args:
            change_id: ID del cambio
            task_data: Datos de la tarea
            current_user_id: ID del usuario actual

        Returns:
            Objeto ChangeTask creado
        """
        task = ChangeTask(
            change_id=change_id,
            title=task_data['title'],
            description=task_data.get('description'),
            order=task_data.get('order', 0),
            is_critical=task_data.get('is_critical', False),
            assigned_to_id=task_data.get('assigned_to_id'),
            status=TaskStatus.PENDING,
            estimated_duration=task_data.get('estimated_duration')
        )

        db.session.add(task)

        ChangeService._add_history(
            change_id,
            'TASK_ADDED',
            None,
            task_data['title'],
            current_user_id,
            'Tarea añadida'
        )

        db.session.commit()

        return task

    @staticmethod
    def add_risk_assessment(change_id: int, risk_data: Dict, current_user_id: int) -> ChangeRiskAssessment:
        """
        Añade evaluación de riesgo al cambio

        Args:
            change_id: ID del cambio
            risk_data: Datos del riesgo
            current_user_id: ID del usuario actual

        Returns:
            Objeto ChangeRiskAssessment creado
        """
        risk = ChangeRiskAssessment(
            change_id=change_id,
            risk_description=risk_data['description'],
            probability=risk_data['probability'],
            impact=risk_data['impact'],
            mitigation_measures=risk_data.get('mitigation_measures'),
            contingency_plan=risk_data.get('contingency_plan'),
            created_by_id=current_user_id
        )

        # El cálculo de risk_score y risk_level se hace en el __init__ del modelo

        db.session.add(risk)
        db.session.commit()

        return risk

    @staticmethod
    def add_review(change_id: int, review_data: Dict, current_user_id: int) -> ChangeReview:
        """
        Añade revisión post-implementación

        Args:
            change_id: ID del cambio
            review_data: Datos de la revisión
            current_user_id: ID del usuario actual

        Returns:
            Objeto ChangeReview creado
        """
        review = ChangeReview(
            change_id=change_id,
            reviewer_id=current_user_id,
            success_status=review_data['success_status'],
            objectives_met=review_data.get('objectives_met'),
            success_criteria_met=review_data.get('success_criteria_met'),
            lessons_learned=review_data.get('lessons_learned'),
            what_went_well=review_data.get('what_went_well'),
            what_went_wrong=review_data.get('what_went_wrong'),
            issues_found=review_data.get('issues_found'),
            recommendations=review_data.get('recommendations'),
            downtime_occurred=review_data.get('downtime_occurred'),
            incidents_caused=review_data.get('incidents_caused'),
            rollback_required=review_data.get('rollback_required', False),
            notes=review_data.get('notes')
        )

        db.session.add(review)

        # Actualizar el cambio con los datos de la revisión
        change = Change.query.get(change_id)
        change.pir_date = datetime.utcnow()
        change.lessons_learned = review_data.get('lessons_learned')
        change.recommendations = review_data.get('recommendations')

        db.session.commit()

        return review

    @staticmethod
    def get_by_status(status: ChangeStatus) -> List[Change]:
        """Obtiene cambios por estado"""
        return Change.query.filter_by(status=status).order_by(Change.requested_date.desc()).all()

    @staticmethod
    def get_pending_approvals(user_id: int) -> List[Change]:
        """Obtiene cambios pendientes de aprobación para un usuario"""
        return Change.query.join(ChangeApproval).filter(
            and_(
                ChangeApproval.approver_id == user_id,
                ChangeApproval.status == ApprovalStatus.PENDING
            )
        ).all()

    @staticmethod
    def get_upcoming_changes(days: int = 7) -> List[Change]:
        """Obtiene cambios programados para los próximos N días"""
        from datetime import timedelta
        future_date = datetime.utcnow() + timedelta(days=days)

        return Change.query.filter(
            and_(
                Change.status == ChangeStatus.SCHEDULED,
                Change.scheduled_start_date <= future_date
            )
        ).order_by(Change.scheduled_start_date).all()

    @staticmethod
    def search(query: str) -> List[Change]:
        """Busca cambios por texto"""
        search_term = f"%{query}%"
        return Change.query.filter(
            or_(
                Change.change_code.ilike(search_term),
                Change.title.ilike(search_term),
                Change.description.ilike(search_term)
            )
        ).order_by(Change.requested_date.desc()).all()

    @staticmethod
    def _add_history(change_id: int, field: str, old_value: str, new_value: str,
                     user_id: int, comments: str = None):
        """Añade entrada al historial de cambios"""
        history = ChangeHistory(
            change_id=change_id,
            field_changed=field,
            old_value=old_value,
            new_value=new_value,
            changed_by_id=user_id,
            comments=comments
        )
        db.session.add(history)
