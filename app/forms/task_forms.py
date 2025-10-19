"""
Formularios para el módulo de Gestión de Tareas
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SelectField, DateTimeField,
    IntegerField, FloatField, BooleanField, SubmitField,
    FieldList, FormField
)
from wtforms.validators import DataRequired, Optional, Length, NumberRange, Email
from datetime import datetime

from app.models.task import TaskFrequency, TaskStatus, TaskPriority, TaskCategory


class TaskTemplateForm(FlaskForm):
    """Formulario para crear/editar plantillas de tareas"""

    title = StringField(
        'Título',
        validators=[DataRequired(message='El título es obligatorio'), Length(max=200)],
        render_kw={'class': 'form-control', 'placeholder': 'Ej: Revisión Trimestral de Controles'}
    )

    description = TextAreaField(
        'Descripción',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe los objetivos y alcance de esta tarea...'}
    )

    category = SelectField(
        'Categoría',
        validators=[DataRequired(message='La categoría es obligatoria')],
        choices=[(cat.value, cat.value.replace('_', ' ').title()) for cat in TaskCategory],
        render_kw={'class': 'form-select'}
    )

    frequency = SelectField(
        'Frecuencia',
        validators=[DataRequired(message='La frecuencia es obligatoria')],
        choices=[(freq.value, freq.value.title()) for freq in TaskFrequency],
        render_kw={'class': 'form-select'}
    )

    priority = SelectField(
        'Prioridad',
        validators=[DataRequired(message='La prioridad es obligatoria')],
        choices=[(pri.value, pri.value.title()) for pri in TaskPriority],
        render_kw={'class': 'form-select'}
    )

    iso_control = StringField(
        'Control ISO 27001',
        validators=[Optional(), Length(max=10)],
        render_kw={'class': 'form-control', 'placeholder': 'Ej: 9.1, 5.37'}
    )

    estimated_hours = FloatField(
        'Horas Estimadas',
        validators=[Optional(), NumberRange(min=0.5, max=1000)],
        render_kw={'class': 'form-control', 'step': '0.5', 'placeholder': '8'}
    )

    default_assignee_id = SelectField(
        'Asignado por Defecto',
        validators=[Optional()],
        coerce=int,
        render_kw={'class': 'form-select'}
    )

    default_role_id = SelectField(
        'Rol Responsable',
        validators=[Optional()],
        coerce=int,
        render_kw={'class': 'form-select'}
    )

    notify_days_before = IntegerField(
        'Notificar con X Días de Antelación',
        validators=[Optional(), NumberRange(min=1, max=90)],
        default=7,
        render_kw={'class': 'form-control', 'placeholder': '7'}
    )

    requires_evidence = BooleanField(
        'Requiere Evidencia Obligatoria',
        render_kw={'class': 'form-check-input'}
    )

    requires_approval = BooleanField(
        'Requiere Aprobación',
        render_kw={'class': 'form-check-input'}
    )

    is_active = BooleanField(
        'Plantilla Activa',
        default=True,
        render_kw={'class': 'form-check-input'}
    )

    submit = SubmitField('Guardar Plantilla', render_kw={'class': 'btn btn-primary'})


class TaskForm(FlaskForm):
    """Formulario para crear/editar tareas manuales"""

    title = StringField(
        'Título',
        validators=[DataRequired(message='El título es obligatorio'), Length(max=200)],
        render_kw={'class': 'form-control', 'placeholder': 'Título de la tarea'}
    )

    description = TextAreaField(
        'Descripción',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción detallada...'}
    )

    category = SelectField(
        'Categoría',
        validators=[DataRequired(message='La categoría es obligatoria')],
        choices=[(cat.value, cat.value.replace('_', ' ').title()) for cat in TaskCategory],
        render_kw={'class': 'form-select'}
    )

    priority = SelectField(
        'Prioridad',
        validators=[DataRequired(message='La prioridad es obligatoria')],
        choices=[(pri.value, pri.value.title()) for pri in TaskPriority],
        render_kw={'class': 'form-select'}
    )

    due_date = DateTimeField(
        'Fecha de Vencimiento',
        validators=[DataRequired(message='La fecha de vencimiento es obligatoria')],
        format='%Y-%m-%d',
        render_kw={'class': 'form-control', 'type': 'date'}
    )

    assigned_to_id = SelectField(
        'Asignar a Usuario',
        validators=[Optional()],
        coerce=int,
        render_kw={'class': 'form-select'}
    )

    assigned_role_id = SelectField(
        'Asignar a Rol',
        validators=[Optional()],
        coerce=int,
        render_kw={'class': 'form-select'}
    )

    iso_control = StringField(
        'Control ISO 27001',
        validators=[Optional(), Length(max=10)],
        render_kw={'class': 'form-control', 'placeholder': 'Ej: 9.1'}
    )

    estimated_hours = FloatField(
        'Horas Estimadas',
        validators=[Optional(), NumberRange(min=0.5, max=1000)],
        render_kw={'class': 'form-control', 'step': '0.5'}
    )

    checklist = TextAreaField(
        'Lista de Verificación (opcional)',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': 5, 'placeholder': 'Una tarea por línea'}
    )

    requires_approval = BooleanField(
        'Requiere Aprobación',
        render_kw={'class': 'form-check-input'}
    )

    submit = SubmitField('Crear Tarea', render_kw={'class': 'btn btn-primary'})


class TaskUpdateForm(FlaskForm):
    """Formulario para actualizar el progreso de una tarea"""

    status = SelectField(
        'Estado',
        validators=[DataRequired()],
        choices=[(status.value, status.value.replace('_', ' ').title()) for status in TaskStatus],
        render_kw={'class': 'form-select'}
    )

    progress = IntegerField(
        'Progreso (%)',
        validators=[Optional(), NumberRange(min=0, max=100)],
        render_kw={'class': 'form-control', 'min': '0', 'max': '100'}
    )

    observations = TextAreaField(
        'Observaciones',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones sobre el progreso...'}
    )

    actual_hours = FloatField(
        'Horas Reales Empleadas',
        validators=[Optional(), NumberRange(min=0)],
        render_kw={'class': 'form-control', 'step': '0.5'}
    )

    submit = SubmitField('Actualizar', render_kw={'class': 'btn btn-primary'})


class TaskCompleteForm(FlaskForm):
    """Formulario para completar una tarea"""

    result = TextAreaField(
        'Resultado de la Tarea',
        validators=[DataRequired(message='Debes documentar el resultado')],
        render_kw={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe el resultado obtenido...'}
    )

    observations = TextAreaField(
        'Observaciones Adicionales',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Cualquier observación relevante...'}
    )

    actual_hours = FloatField(
        'Horas Reales Empleadas',
        validators=[Optional(), NumberRange(min=0)],
        render_kw={'class': 'form-control', 'step': '0.5', 'placeholder': 'Ej: 4.5'}
    )

    submit = SubmitField('Completar Tarea', render_kw={'class': 'btn btn-success'})


class TaskCommentForm(FlaskForm):
    """Formulario para agregar comentarios a una tarea"""

    comment = TextAreaField(
        'Comentario',
        validators=[DataRequired(message='El comentario no puede estar vacío'), Length(min=5)],
        render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Escribe tu comentario...'}
    )

    comment_type = SelectField(
        'Tipo',
        choices=[
            ('general', 'General'),
            ('question', 'Pregunta'),
            ('answer', 'Respuesta'),
            ('observation', 'Observación')
        ],
        default='general',
        render_kw={'class': 'form-select'}
    )

    submit = SubmitField('Agregar Comentario', render_kw={'class': 'btn btn-sm btn-primary'})


class TaskEvidenceForm(FlaskForm):
    """Formulario para subir evidencias"""

    file = FileField(
        'Archivo',
        validators=[
            DataRequired(message='Debes seleccionar un archivo'),
            FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'zip', 'txt'],
                       'Solo se permiten archivos PDF, Word, Excel, imágenes, ZIP y TXT')
        ],
        render_kw={'class': 'form-control'}
    )

    description = TextAreaField(
        'Descripción',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': 2, 'placeholder': 'Describe el contenido del archivo...'}
    )

    submit = SubmitField('Subir Evidencia', render_kw={'class': 'btn btn-primary'})


class TaskFilterForm(FlaskForm):
    """Formulario para filtrar tareas"""

    status = SelectField(
        'Estado',
        choices=[('', 'Todos')] + [(status.value, status.value.replace('_', ' ').title()) for status in TaskStatus],
        render_kw={'class': 'form-select form-select-sm'}
    )

    category = SelectField(
        'Categoría',
        choices=[('', 'Todas')] + [(cat.value, cat.value.replace('_', ' ').title()) for cat in TaskCategory],
        render_kw={'class': 'form-select form-select-sm'}
    )

    priority = SelectField(
        'Prioridad',
        choices=[('', 'Todas')] + [(pri.value, pri.value.title()) for pri in TaskPriority],
        render_kw={'class': 'form-select form-select-sm'}
    )

    assigned_to_id = SelectField(
        'Asignado a',
        choices=[('', 'Todos')],
        coerce=lambda x: int(x) if x else None,
        render_kw={'class': 'form-select form-select-sm'}
    )

    search = StringField(
        'Buscar',
        render_kw={'class': 'form-control form-control-sm', 'placeholder': 'Buscar en tareas...'}
    )

    submit = SubmitField('Filtrar', render_kw={'class': 'btn btn-sm btn-primary'})


class TaskApprovalForm(FlaskForm):
    """Formulario para aprobar/rechazar una tarea"""

    approved = BooleanField(
        'Aprobar Tarea',
        default=True,
        render_kw={'class': 'form-check-input'}
    )

    approval_comments = TextAreaField(
        'Comentarios de Aprobación',
        validators=[Optional()],
        render_kw={'class': 'form-control', 'rows': 3, 'placeholder': 'Comentarios sobre la aprobación...'}
    )

    submit = SubmitField('Confirmar', render_kw={'class': 'btn btn-primary'})
