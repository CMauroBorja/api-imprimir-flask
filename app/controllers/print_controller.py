from flask import Blueprint, jsonify

from app.repositories import order_repository
from app.services.printing.printer_service import (
    imprimir_registro
)
from app.exceptions.custom_exceptions import (
    NotFoundError
)

print_bp = Blueprint(
    "print",
    __name__
)


@print_bp.route(
    "/test-print/<int:registro_id>",
    methods=["GET"]
)
def test_print(registro_id):

    registro = order_repository.get_by_id(
        registro_id
    )

    if not registro:
        raise NotFoundError(
            "Registro no encontrado"
        )

    imprimir_registro(registro)

    return jsonify({
        "success": True,
        "message": "Impresión enviada"
    }), 200