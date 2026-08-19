from app.repositories import order_repository

from app.exceptions.custom_exceptions import (
    NotFoundError
)

from app.services.printing.printer_service import (
    imprimir_registro
)


def print_order(registro_id):

    registro = order_repository.get_by_id(
        registro_id
    )

    if not registro:
        raise NotFoundError(
            "Registro no encontrado"
        )

    imprimir_registro(
        registro
    )

    return {
        "success": True,
        "message": "Impresión enviada"
    }, 200