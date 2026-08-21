from app.config.logging_config import logger
from app.models import Empleado
from app.repositories import employee_repository
from app.security.password_service import hash_password

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

from app.exceptions.custom_exceptions import (
    ValidationError,
    NotFoundError,
    ConflictError
)


def get_all_employees():
    empleados = employee_repository.get_all()
    return serialize_employee_list(empleados), 200


def get_employee_by_id(employee_id):
    empleado = employee_repository.get_by_id(employee_id)
    if not empleado:
        raise NotFoundError("Empleado no encontrado")
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
        raise ValidationError("Datos incompletos para crear empleado")

    if not validar_nombre(data["nombre"]):
        raise ValidationError("Nombre inválido")

    if not validar_telefono(data["telefono"]):
        raise ValidationError("Teléfono inválido")

    if not validar_codigo(data["codigo"]):
        raise ValidationError("Código inválido")

    if not validar_contrasena(data["contrasena"]):
        raise ValidationError("Contraseña inválida")

    empleado_existente = employee_repository.get_by_code(data["codigo"].strip())

    if empleado_existente:       
        raise ConflictError("El código de usuario ya existe")

    try:

        nuevo_empleado = Empleado(
            nombre=data["nombre"].strip(),
            telefono=data["telefono"].strip(),
            codigo=data["codigo"].strip(),
            contrasena=hash_password(data["contrasena"].strip()),
            administrador=bool(data["administrador"])
        )

        employee_repository.add(nuevo_empleado)
        employee_repository.commit()
        
    except Exception:
        employee_repository.rollback()
        raise

    logger.info(
        f"Empleado creado: {nuevo_empleado.codigo}"
    )

    return {
        "message": "Empleado creado exitosamente"
    }, 201


def update_employee(codigo, data):
    
    empleado = employee_repository.get_by_code(codigo)

    if not empleado:
        raise NotFoundError("Empleado no encontrado")

    if "nombre" in data:

        if not validar_nombre(data["nombre"]):
            raise ValidationError("Nombre inválido")

        empleado.nombre = data["nombre"].strip()

    if "telefono" in data:

        if not validar_telefono(data["telefono"]):
            raise ValidationError("Teléfono inválido")

        empleado.telefono = data["telefono"].strip()

    if (
        "contrasena" in data
        and data["contrasena"]
    ):

        if not validar_contrasena(data["contrasena"]):
            raise ValidationError("Contraseña inválida")

        empleado.contrasena = hash_password(
            data["contrasena"].strip()
        )

    if "administrador" in data:
        empleado.administrador = bool(
            data["administrador"]
        )

    try:

        employee_repository.commit()

    except Exception:

        employee_repository.rollback()
        raise

    logger.info(
        f"Empleado actualizado: {empleado.codigo}"
    )

    return {
        "message": "Empleado actualizado correctamente"
    }, 200