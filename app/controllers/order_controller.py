from flask import Blueprint, jsonify, request
from app.models import Registro, Empleado
from app.database.db import db
from app.services.printer_service import imprimir_registro
from datetime import datetime
import re

order_bp = Blueprint("orders", __name__)

def validar_datos_numericos(data):
    try:
        valor_total = float(data["valorTotal"])
        abono = float(data["abono"])
        saldo = float(data["saldo"])

        if valor_total <= 0:
            return False, "El valor total debe ser mayor que 0"

        if abono < 0:
            return False, "El abono no puede ser negativo"

        if saldo < 0:
            return False, "El saldo no puede ser negativo"

        if abs(saldo - (valor_total - abono)) > 0.01:
            return False, (
                "El saldo debe ser igual "
                "al valor total menos el abono"
            )

        return True, ""

    except ValueError:
        return False, (
            "Los valores numéricos son inválidos"
        )

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
        
@order_bp.route("/submitData", methods=["POST"])
def submit_data():
    data = request.json

    required_fields = [
        "nombreCliente",
        "fechaEntrega",
        "valorTotal",
        "abono",
        "saldo",
        "celular",
        "observaciones",
        "vendedor",
        "medioPago"
    ]

    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    if len(data["nombreCliente"].strip()) < 3:
        return jsonify({
            "error": "El nombre del cliente debe tener al menos 3 caracteres"
        }), 400

    if not re.fullmatch(r"\d{10}", data["celular"]):
        return jsonify({
            "error": "El número de celular debe tener 10 dígitos"
        }), 400
        
    valid, error_message = validar_datos_numericos(data)

    if not valid:
        return jsonify({
            "error": error_message
        }), 400

    observaciones_raw = data["observaciones"]

    if isinstance(observaciones_raw, str):
        observaciones_clean = observaciones_raw.strip()
    else:
        observaciones_clean = str(
            observaciones_raw
        ).strip()

    try:
        observaciones = (
            observaciones_clean
            .encode("utf-8")
            .decode("utf-8")
        )
    except UnicodeError:
        return jsonify({
            "error": "Error en la codificación del texto"
        }), 400

    if len(observaciones) < 5:
        return jsonify({
            "error": "Las observaciones deben tener al menos 5 caracteres"
        }), 400

    if len(observaciones) > 500:
        return jsonify({
            "error": "Las observaciones no pueden exceder 500 caracteres"
        }), 400

    vendedor = Empleado.query.filter_by(
        codigo=data["vendedor"]
    ).first()

    if not vendedor:
        return jsonify({
            "error": "El código del vendedor no es válido"
        }), 404

    try:
        ultimo_id = db.session.execute(
            db.text(
                "SELECT ISNULL(MAX(id), 0) FROM arreglos"
            )
        ).scalar()
        
        nuevo_registro = Registro(
            nombreCliente=data["nombreCliente"].strip(),
            fechaEntrega=datetime.strptime(
                data["fechaEntrega"],
                "%Y-%m-%d %H:%M"
            ),
            valorTotal=float(data["valorTotal"]),
            abono=float(data["abono"]),
            saldo=float(data["saldo"]),
            celular=data["celular"],
            telefono=data.get("telefono"),
            observaciones=observaciones,
            vendedor=data["vendedor"].strip(),
            medioPago=data["medioPago"].strip()
        )

        db.session.add(nuevo_registro)
        db.session.flush()
        
        if nuevo_registro.id > (ultimo_id + 2):
            db.session.rollback()

            db.session.execute(
                db.text(
                    f"DBCC CHECKIDENT('arreglos', RESEED, {ultimo_id}"
                    ")"
                )
            )

            db.session.commit()

            return jsonify({
                "error": (
                    "Secuencia de IDs corregida. "
                    "Reintente guardar."
                )
            }), 409

        cantidad_copias = max(
            1,
            int(data.get("cantidadObjetos", 1))
        )

        imprimir_registro(
            nuevo_registro,
            solo_negocio=data.get(
                "tieneWhatsapp",
                False
            ),
            cantidad_copias=cantidad_copias
        )

        db.session.commit()

        return jsonify({
            "message": "Datos guardados correctamente",
            "id": nuevo_registro.id
        }), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "error": f"Error al guardar los datos: {str(e)}"
        }), 500