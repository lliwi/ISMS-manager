"""
Formularios para gestión de usuarios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from utils.validators import (
    PasswordComplexity, NoCommonPasswords, NotSimilarToUsername,
    UniqueEmail, UniqueUsername
)


class UserCreateForm(FlaskForm):
    """Formulario para crear un nuevo usuario"""

    # Información básica
    username = StringField('Nombre de Usuario',
                          validators=[
                              DataRequired(message='El nombre de usuario es obligatorio'),
                              Length(min=3, max=80, message='Debe tener entre 3 y 80 caracteres'),
                              UniqueUsername()
                          ],
                          render_kw={'placeholder': 'usuario', 'autocomplete': 'off'})

    email = StringField('Correo Electrónico',
                       validators=[
                           DataRequired(message='El correo electrónico es obligatorio'),
                           Email(message='Ingresa un correo electrónico válido'),
                           UniqueEmail(model='User')
                       ],
                       render_kw={'placeholder': 'usuario@ejemplo.com', 'type': 'email'})

    # Información personal
    first_name = StringField('Nombre',
                            validators=[
                                DataRequired(message='El nombre es obligatorio'),
                                Length(max=100)
                            ],
                            render_kw={'placeholder': 'Juan'})

    last_name = StringField('Apellidos',
                           validators=[
                               DataRequired(message='Los apellidos son obligatorios'),
                               Length(max=100)
                           ],
                           render_kw={'placeholder': 'Pérez García'})

    phone = StringField('Teléfono',
                       validators=[Optional(), Length(max=20)],
                       render_kw={'placeholder': '+34 600 000 000', 'type': 'tel'})

    department = StringField('Departamento',
                            validators=[Optional(), Length(max=100)],
                            render_kw={'placeholder': 'TI, RRHH, Operaciones...'})

    position = StringField('Cargo',
                          validators=[Optional(), Length(max=100)],
                          render_kw={'placeholder': 'Desarrollador, Analista...'})

    # Rol y permisos
    role_id = SelectField('Rol',
                         coerce=int,
                         validators=[DataRequired(message='Debes seleccionar un rol')])

    # Contraseña
    password = PasswordField('Contraseña',
                            validators=[
                                DataRequired(message='La contraseña es obligatoria'),
                                PasswordComplexity(min_length=8),
                                NoCommonPasswords(),
                                NotSimilarToUsername(username_field='username')
                            ],
                            render_kw={'placeholder': '••••••••', 'autocomplete': 'new-password'})

    password_confirm = PasswordField('Confirmar Contraseña',
                                    validators=[
                                        DataRequired(message='Debes confirmar la contraseña'),
                                        EqualTo('password', message='Las contraseñas no coinciden')
                                    ],
                                    render_kw={'placeholder': '••••••••', 'autocomplete': 'new-password'})

    # Opciones
    is_active = BooleanField('Usuario Activo', default=True)
    must_change_password = BooleanField('Debe cambiar contraseña en el primer login', default=True)


class UserEditForm(FlaskForm):
    """Formulario para editar un usuario existente"""

    user_id = HiddenField('User ID')

    # Información básica (username no editable)
    username = StringField('Nombre de Usuario',
                          render_kw={'readonly': True, 'disabled': True})

    email = StringField('Correo Electrónico',
                       validators=[
                           DataRequired(message='El correo electrónico es obligatorio'),
                           Email(message='Ingresa un correo electrónico válido'),
                           UniqueEmail(model='User')
                       ],
                       render_kw={'placeholder': 'usuario@ejemplo.com', 'type': 'email'})

    # Información personal
    first_name = StringField('Nombre',
                            validators=[
                                DataRequired(message='El nombre es obligatorio'),
                                Length(max=100)
                            ])

    last_name = StringField('Apellidos',
                           validators=[
                               DataRequired(message='Los apellidos son obligatorios'),
                               Length(max=100)
                           ])

    phone = StringField('Teléfono',
                       validators=[Optional(), Length(max=20)],
                       render_kw={'type': 'tel'})

    department = StringField('Departamento',
                            validators=[Optional(), Length(max=100)])

    position = StringField('Cargo',
                          validators=[Optional(), Length(max=100)])

    # Rol y permisos
    role_id = SelectField('Rol',
                         coerce=int,
                         validators=[DataRequired(message='Debes seleccionar un rol')])

    # Estado
    is_active = BooleanField('Usuario Activo')


class ChangePasswordForm(FlaskForm):
    """Formulario para cambio de contraseña"""

    current_password = PasswordField('Contraseña Actual',
                                    validators=[DataRequired(message='Ingresa tu contraseña actual')],
                                    render_kw={'placeholder': '••••••••', 'autocomplete': 'current-password'})

    new_password = PasswordField('Nueva Contraseña',
                                validators=[
                                    DataRequired(message='Ingresa la nueva contraseña'),
                                    PasswordComplexity(min_length=8),
                                    NoCommonPasswords()
                                ],
                                render_kw={'placeholder': '••••••••', 'autocomplete': 'new-password'})

    new_password_confirm = PasswordField('Confirmar Nueva Contraseña',
                                        validators=[
                                            DataRequired(message='Confirma la nueva contraseña'),
                                            EqualTo('new_password', message='Las contraseñas no coinciden')
                                        ],
                                        render_kw={'placeholder': '••••••••', 'autocomplete': 'new-password'})


class ResetPasswordForm(FlaskForm):
    """Formulario para resetear contraseña de un usuario (admin)"""

    new_password = PasswordField('Nueva Contraseña',
                                validators=[
                                    DataRequired(message='Ingresa la nueva contraseña'),
                                    PasswordComplexity(min_length=8),
                                    NoCommonPasswords()
                                ],
                                render_kw={'placeholder': '••••••••', 'autocomplete': 'new-password'})

    new_password_confirm = PasswordField('Confirmar Nueva Contraseña',
                                        validators=[
                                            DataRequired(message='Confirma la nueva contraseña'),
                                            EqualTo('new_password', message='Las contraseñas no coinciden')
                                        ],
                                        render_kw={'placeholder': '••••••••', 'autocomplete': 'new-password'})

    must_change_password = BooleanField('El usuario debe cambiar la contraseña en el próximo login',
                                       default=True)

    notify_user = BooleanField('Notificar al usuario por correo electrónico',
                              default=False)


class UserSearchForm(FlaskForm):
    """Formulario de búsqueda y filtrado de usuarios"""

    search = StringField('Buscar',
                        validators=[Optional()],
                        render_kw={'placeholder': 'Buscar por nombre, usuario o email...'})

    role = SelectField('Rol',
                      coerce=int,
                      validators=[Optional()],
                      choices=[])  # Se llenarán dinámicamente

    status = SelectField('Estado',
                        choices=[
                            ('', 'Todos'),
                            ('active', 'Activos'),
                            ('inactive', 'Inactivos')
                        ],
                        validators=[Optional()])

    department = StringField('Departamento',
                            validators=[Optional()])
