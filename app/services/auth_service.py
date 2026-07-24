from app.repositories import employee_repository
from app.config.logging_config import logger
from app.security.password_service import verify_password
from app.validators.auth_validator import (
    validar_login
)


def login_user(data):

    valid, error = validar_login(data)

    if not valid:
        logger.warning(
            f"Intento de login inválido: {error}"
        )

        return {
            "error": error
        }, 400

    empleado = employee_repository.get_by_code(
        data["codigo"].strip()
    )

    if not empleado:

        logger.warning(
            f"Intento de login con código inexistente: {data['codigo']}"
        )

        return {
            "error":
            "El codigo de usuario no es valido"
        }, 404

    if (
        not verify_password(data["contrasena"].strip(), empleado.contrasena)
    ):

        logger.warning(
            f"Contraseña incorrecta para el usuario: {empleado.codigo}"
        )

        return {
            "error":
            "La contraseña es incorrecta"
        }, 401

    logger.info(
        f"Login exitoso: {empleado.codigo}"
    )

    return {
        "message":
        "Inicio de sesión exitoso",
        "nombre":
        empleado.nombre,
        "codigo":
        empleado.codigo,
        "administrador":
        empleado.administrador
    }, 200