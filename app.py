from flask import request, jsonify
from datetime import datetime
import os, re, time, logging, unicodedata
import win32print

from app.database.db import db
from app.models import Empleado, Registro
from app.services.printer_service import (
    imprimir_registro,
    imprimir_solo_cliente
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    
@app.route("/updateEmployee/<codigo>", methods=["PUT"])
def update_employee(codigo):
    data = request.json
    empleado = Empleado.query.filter_by(codigo=codigo).first()
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404

    if "nombre" in data:
        empleado.nombre = data["nombre"].strip()
    if "telefono" in data:
        empleado.telefono = data["telefono"].strip()
    if "contrasena" in data and data["contrasena"]:
        empleado.contrasena = data["contrasena"].strip()
    if "administrador" in data:
        empleado.administrador = bool(data["administrador"])

    db.session.commit()
    return jsonify({"message": "Empleado actualizado correctamente"}), 200

@app.route("/deleteOrder/<int:id>", methods=["DELETE"])
def eliminar_orden(id):
    try:
        registro = Registro.query.get(id)
        if not registro:
            return jsonify({"error": "Orden no encontrada"}), 404

        db.session.delete(registro)
        db.session.commit()
        return jsonify({"message": "Orden eliminada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al eliminar la orden: {str(e)}"}), 500

@app.route("/updateOrder/<int:id>", methods=["PUT"])
def actualizar_orden(id):
    data = request.json
    try:
        registro = Registro.query.get(id)
        if not registro:
            return jsonify({"error": "Orden no encontrada"}), 404

        # Validar datos numéricos si se actualizan
        if any(key in data for key in ["valorTotal", "abono", "saldo"]):
            # Crear diccionario con valores actuales y actualizados
            valores = {
                "valorTotal": float(data.get("valorTotal", registro.valorTotal)),
                "abono": float(data.get("abono", registro.abono)),
                "saldo": float(data.get("saldo", registro.saldo))
            }
            valid, error_message = validar_datos_numericos(valores)
            if not valid:
                return jsonify({"error": error_message}), 400

        # Actualizar campos con validaciones
        if "nombreCliente" in data:
            if len(data["nombreCliente"].strip()) < 3:
                return jsonify({"error": "El nombre del cliente debe tener al menos 3 caracteres"}), 400
            registro.nombreCliente = data["nombreCliente"].strip()

        if "fechaEntrega" in data:
            registro.fechaEntrega = datetime.strptime(data["fechaEntrega"], "%Y-%m-%d %H:%M")
        if "valorTotal" in data:
            registro.valorTotal = float(data["valorTotal"])
        if "abono" in data:
            registro.abono = float(data["abono"])
        if "saldo" in data:
            registro.saldo = float(data["saldo"])
        if "celular" in data:
            if not re.fullmatch(r"\d{10}", data["celular"]):
                return jsonify({"error": "El número de celular debe tener exactamente 10 dígitos"}), 400
            registro.celular = data["celular"]
        if "telefono" in data:
            registro.telefono = data["telefono"]
        if "observaciones" in data:
            registro.observaciones = data["observaciones"]
        if "finalizada" in data:
            registro.finalizada = bool(data["finalizada"]) 

        db.session.commit()
        return jsonify({"message": "Orden actualizada correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar la orden: {str(e)}"}), 500

@app.route("/reprintOrder/<int:id>", methods=["POST"])
def reimprimir_orden(id):
    data = request.json
    reprint_type = data.get("reprintType", "1")
    
    try:
        # Buscar la orden en la base de datos
        registro = Registro.query.get(id)
        if not registro:
            return jsonify({"error": "Orden no encontrada"}), 404

        # Determinar qué imprimir según el tipo
        if reprint_type == "1":  # Cliente y Negocio
            imprimir_registro(registro, solo_negocio=False, cantidad_copias=1)
            message = "Reimpresas: copia del cliente y copia del negocio"
        elif reprint_type == "2":  # Solo Cliente
            imprimir_solo_cliente(registro)
            message = "Reimpresa: solo copia del cliente"
        elif reprint_type == "3":  # Solo Negocio
            imprimir_registro(registro, solo_negocio=True, cantidad_copias=1)
            message = "Reimpresa: solo copia del negocio"
        else:
            return jsonify({"error": "Tipo de reimpresión inválido"}), 400

        return jsonify({"message": message}), 200
        
    except Exception as e:
        return jsonify({"error": f"Error al reimprimir la orden: {str(e)}"}), 500
