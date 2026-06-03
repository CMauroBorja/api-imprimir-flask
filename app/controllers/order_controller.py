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
    try:
        return jsonify(get_all_orders()), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
        
@order_bp.route("/submitData", methods=["POST"])
def submit_data():

    try:
        response, status = create_order(request.json)

        return jsonify(response), status

    except Exception as e:
        return jsonify({
            "error":
            f"Error al guardar los datos: {str(e)}"
        }), 500
        
@order_bp.route("/reprintOrder/<int:id>", methods=["POST"])
def reprint_order(id):
    data = request.json
    reprint_type = data.get("reprintType", "1")

    try:
        response, status = reprint_order_by_id(id, reprint_type)
        return jsonify(response), status

    except Exception as e:
        return jsonify({
            "error":
            f"Error al reimprimir la orden: {str(e)}"
        }), 500
        
@order_bp.route("/deleteOrder/<int:id>", methods=["DELETE"])
def delete_order(id):
    try:
        response, status = delete_order_by_id(id)
        return jsonify(response), status

    except Exception as e:
        return jsonify({
            "error": (
            f"Error al eliminar la orden: {str(e)}"
            )
        }), 500
        
@order_bp.route("/updateOrder/<int:id>", methods=["PUT"])
def actualizar_orden(id):
    data = request.json
    
    try:
        response, status = update_order(id, data)
        return jsonify(response), status
    except Exception as e:
        return jsonify({
            "error": f"Error al actualizar la orden: {str(e)}"
        }), 500