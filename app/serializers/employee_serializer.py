def serialize_employee(empleado):
    return {
        "id": empleado.id,
        "nombre": empleado.nombre,
        "telefono": empleado.telefono,
        "codigo": empleado.codigo,
        "administrador": empleado.administrador
    }


def serialize_employee_list(empleados):
    return [
        serialize_employee(empleado)
        for empleado in empleados
    ]