from flask import Blueprint, jsonify
from app.models import Registro

order_bp = Blueprint("orders", __name__)


@order_bp.route("/getOrders", methods=["GET"])
def get_orders():
    try:
        registros = Registro.query.order_by(
            Registro.fechaCreacion.desc()
        ).all()

        resultado = [
            {
                "id": r.id,
                "nombreCliente": r.nombreCliente,
                "fechaEntrega": r.fechaEntrega.strftime("%Y-%m-%d %H:%M"),
                "fechaCreacion": r.fechaCreacion.strftime("%Y-%m-%d %H:%M"),
                "valorTotal": float(r.valorTotal),
                "abono": float(r.abono),
                "saldo": float(r.saldo),
                "celular": r.celular,
                "telefono": r.telefono,
                "observaciones": r.observaciones,
                "vendedor": r.vendedor,
                "finalizada": r.finalizada
            }
            for r in registros
        ]

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500