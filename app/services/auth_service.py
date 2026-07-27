from app.repositories import employee_repository
from app.config.logging_config import logger
from app.security.password_service import verify_password
from app.validators.auth_validator import validar_login

from app.exceptions.custom_exceptions import (
    ValidationError,
    NotFoundError,
    UnauthorizedError
)


def login_user(data):

    valid, error = validar_login(data)

    if not valid:
        raise ValidationError(error)

    empleado = employee_repository.get_by_code(
        data["codigo"].strip()
    )

    if not empleado:
        raise NotFoundError(
            "El código de usuario no es válido"
        )

    if not verify_password(
        data["contrasena"].strip(),
        empleado.contrasena
    ):
        raise UnauthorizedError(
            "La contraseña es incorrecta"
        )

    logger.info(
        f"Login exitoso: {empleado.codigo}"
    )

    return {
        "message": "Inicio de sesión exitoso",
        "nombre": empleado.nombre,
        "codigo": empleado.codigo,
        "administrador": empleado.administrador
    }, 200