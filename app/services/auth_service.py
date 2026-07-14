from app.repositories import employee_repository

from app.validators.auth_validator import (
    validar_login
)


def login_user(data):

    valid, error = validar_login(data)

    if not valid:
        return {
            "error": error
        }, 400

    empleado = employee_repository.get_by_code(
        data["codigo"].strip()
    )

    if not empleado:
        return {
            "error":
            "El codigo de usuario no es valido"
        }, 404

    if (
        empleado.contrasena
        != data["contrasena"].strip()
    ):
        return {
            "error":
            "La contraseña es incorrecta"
        }, 401

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