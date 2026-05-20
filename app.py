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

# 5. Funciones auxiliares
def validar_datos_numericos(data):
    """Valida los valores numéricos y su relación"""
    try:
        valor_total = float(data["valorTotal"])
        abono = float(data["abono"])
        saldo = float(data["saldo"])

        # Validar valores positivos
        if valor_total <= 0:
            return False, "El valor total debe ser mayor que 0"
        if abono < 0:
            return False, "El abono no puede ser negativo"
        if saldo < 0:
            return False, "El saldo no puede ser negativo"

        # Validar que saldo = valorTotal - abono
        if abs(saldo - (valor_total - abono)) > 0.01:
            return False, "El saldo debe ser igual al valor total menos el abono"

        return True, ""
    except ValueError:
        return False, "Los valores numéricos son inválidos"

@app.route("/createEmployee", methods=["POST"])
def crear_empleado():
    data = request.json
    required_fields = ["nombre", "telefono", "codigo", "contrasena", "administrador"]

    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    try:
        nuevo_empleado = Empleado(
            nombre=data["nombre"].strip(),
            telefono=data["telefono"].strip(),
            codigo=data["codigo"].strip(),
            contrasena=data["contrasena"].strip(),
            administrador=bool(data["administrador"])
        )
        db.session.add(nuevo_empleado)
        db.session.commit()
        return jsonify({"message": "Empleado creado correctamente", "id": nuevo_empleado.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al crear el empleado: {str(e)}"}), 500

@app.route("/getEmployee/<codigo>", methods=["GET"])
def get_employee(codigo):
    empleado = Empleado.query.filter_by(codigo=codigo).first()
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404
    return jsonify({
        "nombre": empleado.nombre,
        "telefono": empleado.telefono,
        "codigo": empleado.codigo,
        "administrador": empleado.administrador
    }), 200
    
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

@app.route("/submitData", methods=["POST"])
def recibir_datos():
    data = request.json
    required_fields = ["nombreCliente", "fechaEntrega", "valorTotal", "abono", "saldo", "celular", "observaciones", "vendedor", "medioPago"]

    # Validar campos requeridos
    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    # Validar longitud mínima del nombre
    if len(data["nombreCliente"].strip()) < 3:
        return jsonify({"error": "El nombre del cliente debe tener al menos 3 caracteres"}), 400

    # Validar celular
    if not re.fullmatch(r"\d{10}", data["celular"]):
        return jsonify({"error": "El número de celular debe tener exactamente 10 dígitos"}), 400

    # Validar valores numéricos
    valid, error_message = validar_datos_numericos(data)
    if not valid:
        return jsonify({"error": error_message}), 400

    # Procesar observaciones con mejor manejo de codificación
    observaciones_raw = data["observaciones"]
    #logger.info(f"🔍 Observaciones recibidas (raw): '{observaciones_raw}'")
    #logger.info(f"🔍 Longitud original: {len(observaciones_raw)}")
    
    # Asegurar que sea string y limpiar espacios
    if isinstance(observaciones_raw, str):
        observaciones_clean = observaciones_raw.strip()
    else:
        observaciones_clean = str(observaciones_raw).strip()
    
    #logger.info(f"🔍 Observaciones después de strip: '{observaciones_clean}'")
    #logger.info(f"🔍 Longitud después de strip: {len(observaciones_clean)}")
    
    # Validar longitud mínima
    if len(observaciones_clean) < 5:
        return jsonify({"error": "Las observaciones deben tener al menos 5 caracteres"}), 400

    # Validar longitud máxima
    if len(observaciones_clean) > 500:
        return jsonify({"error": "Las observaciones no pueden exceder 500 caracteres"}), 400

    # Asegurar codificación UTF-8 correcta
    try:
        # Intentar codificar y decodificar para asegurar integridad
        observaciones_final = observaciones_clean.encode('utf-8').decode('utf-8')
        #logger.info(f"🔍 Observaciones finales: '{observaciones_final}'")
        #logger.info(f"🔍 Longitud final: {len(observaciones_final)}")
    except UnicodeError as e:
        #logger.error(f"❌ Error de codificación: {e}")
        return jsonify({"error": "Error en la codificación del texto"}), 400

    # Validar que el vendedor exista
    vendedor = Empleado.query.filter_by(codigo=data["vendedor"]).first()
    if not vendedor:
        return jsonify({"error": "El código del vendedor no es válido"}), 404

    try:
        ultimo_id = db.session.execute(db.text("SELECT ISNULL(MAX(id), 0) FROM arreglos")).scalar()

        nuevo_registro = Registro(
            nombreCliente=data["nombreCliente"].strip(),
            fechaEntrega=datetime.strptime(data["fechaEntrega"], "%Y-%m-%d %H:%M"),
            valorTotal=float(data["valorTotal"]),
            abono=float(data["abono"]),
            saldo=float(data["saldo"]),
            celular=data["celular"],
            telefono=data.get("telefono"),
            observaciones=observaciones_final,  # Usar la versión procesada
            vendedor=data["vendedor"].strip(),
            medioPago=data["medioPago"].strip()
        )
        db.session.add(nuevo_registro)
        db.session.flush()  # genera el ID pero aún no guarda permanentemente

        # Verificar lo que realmente se guardó antes de continuar
        #logger.info(f"🔍 Verificación en DB antes del commit:")
        #logger.info(f"🔍 ID: {nuevo_registro.id}")
        #logger.info(f"🔍 Observaciones guardadas: '{nuevo_registro.observaciones}'")
        #logger.info(f"🔍 Longitud guardada: {len(nuevo_registro.observaciones or '')}")

        # Verificar salto
        if nuevo_registro.id > (ultimo_id + 2):  # Permitir salto de 1
            #logger.warning(f"🚨 Salto detectado: de {ultimo_id} a {nuevo_registro.id}")
            
            # Opción A: Corregir y reintentar
            db.session.rollback()
            db.session.execute(db.text(f"DBCC CHECKIDENT('arreglos', RESEED, {ultimo_id})"))
            db.session.commit()
            
            # Reintentar una vez
            return recibir_datos()
        
        # Obtener cantidad de copias (mínimo 1)
        cantidad_copias = max(1, int(data.get("cantidadObjetos", 1)))
        imprimir_registro(nuevo_registro,solo_negocio=data.get("tieneWhatsapp", False), cantidad_copias=cantidad_copias)
        db.session.commit()
        
        # Verificación final después del commit
        registro_guardado = Registro.query.get(nuevo_registro.id)
        #logger.info(f"🔍 Verificación final después del commit:")
        #logger.info(f"🔍 Observaciones en DB: '{registro_guardado.observaciones}'")
        #logger.info(f"🔍 Longitud en DB: {len(registro_guardado.observaciones or '')}")
        
        return jsonify({"message": "Datos guardados correctamente","id": nuevo_registro.id}), 201
    except Exception as e:
        db.session.rollback()
        #logger.error(f"❌ Error al guardar: {str(e)}")
        return jsonify({"error": f"Error al guardar los datos: {str(e)}"}), 500

@app.route("/getOrders", methods=["GET"])
def obtener_ordenes():
    try:
        registros = Registro.query.order_by(Registro.fechaCreacion.desc()).all()
        
        resultado = [
            {
                "id": registro.id,
                "nombreCliente": registro.nombreCliente,
                "fechaEntrega": registro.fechaEntrega.strftime('%Y-%m-%d %H:%M'),
                "fechaCreacion": registro.fechaCreacion.strftime('%Y-%m-%d %H:%M'),
                "valorTotal": float(registro.valorTotal),
                "abono": float(registro.abono),
                "saldo": float(registro.saldo),
                "celular": registro.celular,
                "telefono": registro.telefono,
                "observaciones": registro.observaciones,
                "vendedor": registro.vendedor,
                "finalizada": registro.finalizada 
            }
            for registro in registros
        ]
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener las órdenes: {str(e)}"}), 500

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
