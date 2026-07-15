from app.models import Empleado
from app.repositories import employee_repository

from app.validators.employee_validator import (
    validar_nombre,
    validar_telefono,
    validar_codigo,
    validar_contrasena
)

from app.serializers import (
    serialize_employee,
    serialize_employee_list
)


def get_all_employees():
    empleados = employee_repository.get_all()

    return serialize_employee_list(empleados), 200

def get_employee_by_id(employee_id):
    empleado = employee_repository.get_by_id(employee_id)

    if not empleado:
        return {
            "error": "Empleado no encontrado"
        }, 404

    return serialize_employee(empleado), 200


def create_employee(data):

    required_fields = [
        "nombre",
        "telefono",
        "codigo",
        "contrasena",
        "administrador"
    ]

    if not data or any(
        field not in data
        for field in required_fields
    ):
        return {
            "error": "Faltan datos requeridos"
        }, 400

    if not validar_nombre(data["nombre"]):
        return {
            "error": "Nombre inválido"
        }, 400

    if not validar_telefono(data["telefono"]):
        return {
            "error": "Teléfono inválido"
        }, 400

    if not validar_codigo(data["codigo"]):
        return {
            "error": "Código inválido"
        }, 400

    if not validar_contrasena(data["contrasena"]):
        return {
            "error": "Contraseña inválida"
        }, 400

    empleado_existente = employee_repository.get_by_code(data["codigo"].strip())

    if empleado_existente:
        return {
            "error": "El código de usuario ya existe"
        }, 409

    try:

        nuevo_empleado = Empleado(
            nombre=data["nombre"].strip(),
            telefono=data["telefono"].strip(),
            codigo=data["codigo"].strip(),
            contrasena=data["contrasena"].strip(),
            administrador=bool(data["administrador"])
        )

        employee_repository.add(nuevo_empleado)
        employee_repository.commit()

        return {
            "message": "Empleado creado exitosamente"
        }, 201

    except Exception:
        employee_repository.rollback()
        raise


def update_employee(codigo, data):

    try:

        empleado = employee_repository.get_by_code(codigo)

        if not empleado:
            return {
                "error": "Empleado no encontrado"
            }, 404

        if "nombre" in data:

            if not validar_nombre(data["nombre"]):
                return {
                    "error": "Nombre inválido"
                }, 400

            empleado.nombre = data["nombre"].strip()

        if "telefono" in data:

            if not validar_telefono(data["telefono"]):
                return {
                    "error": "Teléfono inválido"
                }, 400

            empleado.telefono = data["telefono"].strip()

        if (
            "contrasena" in data
            and data["contrasena"]
        ):

            if not validar_contrasena(data["contrasena"]):
                return {
                    "error": "Contraseña inválida"
                }, 400

            empleado.contrasena = data["contrasena"].strip()

        if "administrador" in data:
            empleado.administrador = bool(
                data["administrador"]
            )

        employee_repository.commit()

        return {
            "message": "Empleado actualizado correctamente"
        }, 200

    except Exception:
        employee_repository.rollback()
        raise