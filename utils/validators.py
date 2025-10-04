"""
Validadores de contraseñas y otros campos de seguridad
"""
import re
from wtforms.validators import ValidationError


class PasswordComplexity:
    """
    Validador de complejidad de contraseñas para ISO 27001

    Requisitos:
    - Mínimo 8 caracteres (configurable)
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    - Al menos 1 carácter especial
    """

    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True,
                 require_digit=True, require_special=True, message=None):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.message = message

    def __call__(self, form, field):
        password = field.data
        errors = []

        if len(password) < self.min_length:
            errors.append(f'al menos {self.min_length} caracteres')

        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append('al menos una letra mayúscula')

        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append('al menos una letra minúscula')

        if self.require_digit and not re.search(r'\d', password):
            errors.append('al menos un número')

        if self.require_special and not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            errors.append('al menos un carácter especial (!@#$%^&*...)')

        if errors:
            if self.message:
                message = self.message
            else:
                message = f'La contraseña debe contener {", ".join(errors)}'
            raise ValidationError(message)


class NoCommonPasswords:
    """
    Validador que rechaza contraseñas comunes
    """

    COMMON_PASSWORDS = {
        'password', 'password123', '12345678', 'qwerty', 'abc123',
        '123456', '123456789', 'letmein', 'welcome', 'monkey',
        'admin', 'admin123', 'root', 'toor', 'pass', 'test',
        '1234', '12345', 'password1', 'qwerty123', 'welcome123'
    }

    def __init__(self, message=None):
        if message is None:
            message = 'Esta contraseña es demasiado común. Por favor, elige una más segura.'
        self.message = message

    def __call__(self, form, field):
        password = field.data.lower()
        if password in self.COMMON_PASSWORDS:
            raise ValidationError(self.message)


class NotSimilarToUsername:
    """
    Validador que verifica que la contraseña no sea similar al username
    """

    def __init__(self, username_field='username', message=None):
        self.username_field = username_field
        if message is None:
            message = 'La contraseña no debe ser similar a tu nombre de usuario.'
        self.message = message

    def __call__(self, form, field):
        password = field.data.lower()
        username = getattr(form, self.username_field, None)

        if username and username.data:
            username_lower = username.data.lower()
            # Verificar si el username está contenido en la password o viceversa
            if username_lower in password or password in username_lower:
                raise ValidationError(self.message)


class UniqueEmail:
    """
    Validador que verifica que el email sea único
    """

    def __init__(self, model, exclude_id=None, message=None):
        self.model = model
        self.exclude_id = exclude_id
        if message is None:
            message = 'Este correo electrónico ya está registrado.'
        self.message = message

    def __call__(self, form, field):
        from models import User

        query = User.query.filter_by(email=field.data)

        # Si estamos editando, excluir el usuario actual
        if hasattr(form, 'user_id') and form.user_id.data:
            query = query.filter(User.id != form.user_id.data)

        if query.first():
            raise ValidationError(self.message)


class UniqueUsername:
    """
    Validador que verifica que el username sea único
    """

    def __init__(self, message=None):
        if message is None:
            message = 'Este nombre de usuario ya está en uso.'
        self.message = message

    def __call__(self, form, field):
        from models import User

        query = User.query.filter_by(username=field.data)

        # Si estamos editando, excluir el usuario actual
        if hasattr(form, 'user_id') and form.user_id.data:
            query = query.filter(User.id != form.user_id.data)

        if query.first():
            raise ValidationError(self.message)


def validate_password_strength(password):
    """
    Función auxiliar para validar la fortaleza de una contraseña
    Retorna (is_valid, errors_list, strength_score)
    """
    errors = []
    score = 0

    # Longitud
    if len(password) < 8:
        errors.append('La contraseña debe tener al menos 8 caracteres')
    else:
        score += 1
        if len(password) >= 12:
            score += 1

    # Mayúsculas
    if not re.search(r'[A-Z]', password):
        errors.append('Debe contener al menos una letra mayúscula')
    else:
        score += 1

    # Minúsculas
    if not re.search(r'[a-z]', password):
        errors.append('Debe contener al menos una letra minúscula')
    else:
        score += 1

    # Números
    if not re.search(r'\d', password):
        errors.append('Debe contener al menos un número')
    else:
        score += 1

    # Caracteres especiales
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        errors.append('Debe contener al menos un carácter especial')
    else:
        score += 1

    # Diversidad de caracteres
    if len(set(password)) < 5:
        errors.append('La contraseña debe tener más variedad de caracteres')
    else:
        score += 1

    is_valid = len(errors) == 0
    strength = 'Débil' if score < 3 else 'Media' if score < 5 else 'Fuerte'

    return is_valid, errors, score, strength
