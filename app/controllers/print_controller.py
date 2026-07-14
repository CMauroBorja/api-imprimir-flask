from flask import Blueprint, jsonify

from app.repositories import order_repository
from app.services.printing.printer_service import (
    imprimir_registro
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

    try:

        registro = order_repository.get_by_id(
            registro_id
        )

        if not registro:
            return jsonify({
                "success": False,
                "error": "Registro no encontrado"
            }), 404

        imprimir_registro(registro)

        return jsonify({
            "success": True,
            "message": "Impresión enviada"
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500