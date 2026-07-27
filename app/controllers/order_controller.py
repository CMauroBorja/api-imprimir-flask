from flask import Blueprint, jsonify, request

from app.services.order_service import (
    get_all_orders,
    delete_order_by_id,
    reprint_order_by_id,
    update_order,
    create_order
)

order_bp = Blueprint("orders", __name__)


@order_bp.route("/getOrders", methods=["GET"])
def get_orders():

    response, status = get_all_orders()

    return jsonify(response), status


@order_bp.route("/submitData", methods=["POST"])
def submit_data():

    response, status = create_order(
        request.json
    )

    return jsonify(response), status


@order_bp.route("/reprintOrder/<int:id>", methods=["POST"])
def reprint_order(id):

    data = request.json
    reprint_type = data.get(
        "reprintType",
        "1"
    )

    response, status = reprint_order_by_id(
        id,
        reprint_type
    )

    return jsonify(response), status


@order_bp.route("/deleteOrder/<int:id>", methods=["DELETE"])
def delete_order(id):

    response, status = delete_order_by_id(id)

    return jsonify(response), status


@order_bp.route("/updateOrder/<int:id>", methods=["PUT"])
def actualizar_orden(id):

    response, status = update_order(
        id,
        request.json
    )

    return jsonify(response), status