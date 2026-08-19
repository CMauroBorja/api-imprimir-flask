from flask import Blueprint, jsonify

from app.services.print_service import (
    print_order
)


print_bp = Blueprint(
    "print",
    __name__
)


@print_bp.route(
    "/print-order/<int:registro_id>",
    methods=["POST"]
)
def print_order_route(registro_id):

    response, status = print_order(
        registro_id
    )

    return jsonify(response), status