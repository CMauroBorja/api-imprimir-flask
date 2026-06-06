from app.models import Empleado
from app.database.db import db

from app.validators.employee_validator import (
    validar_nombre,
    validar_telefono,
    validar_codigo,
    validar_contrasena
)


def get_all_employees():
    empleados = Empleado.query.all()

    return [
        {
            "id": empleado.id,
            "nombre": empleado.nombre,
            "telefono": empleado.telefono,
            "codigo": empleado.codigo,
            "administrador": empleado.administrador
        }
        for empleado in empleados
    ]


def get_employee_by_id(employee_id):
    empleado = Empleado.query.get(employee_id)

    if not empleado:
        return {
            "error": "Empleado no encontrado"
        }, 404

    return {
        "id": empleado.id,
        "nombre": empleado.nombre,
        "telefono": empleado.telefono,
        "codigo": empleado.codigo,
        "administrador": empleado.administrador
    }, 200


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

    empleado_existente = Empleado.query.filter_by(
        codigo=data["codigo"].strip()
    ).first()

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

        db.session.add(nuevo_empleado)
        db.session.commit()

        return {
            "message": "Empleado creado exitosamente"
        }, 201

    except Exception:
        db.session.rollback()
        raise


def update_employee(codigo, data):

    try:

        empleado = Empleado.query.filter_by(
            codigo=codigo
        ).first()

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

        db.session.commit()

        return {
            "message": "Empleado actualizado correctamente"
        }, 200

    except Exception:
        db.session.rollback()
        raise