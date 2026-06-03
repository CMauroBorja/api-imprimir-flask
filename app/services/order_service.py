from app.models import Registro, Empleado
from app.database.db import db
from datetime import datetime
import re
from app.services.printing.printer_service import (
    imprimir_registro,
    imprimir_solo_cliente
)


def get_all_orders():
    registros = Registro.query.order_by(
        Registro.fechaCreacion.desc()
    ).all()

    return [
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
    

def delete_order_by_id(order_id):
    try:
        registro = Registro.query.get(order_id)

        if not registro:
            return {
                "error": "Orden no encontrada"
            }, 404

        db.session.delete(registro)
        db.session.commit()

        return {
            "message": "Orden eliminada correctamente"
        }, 200
    except Exception as e:
        db.session.rollback()
        raise
    
    
def reprint_order_by_id(order_id, reprint_type):
    registro = Registro.query.get(order_id)

    if not registro:
        return {
            "error": "Orden no encontrada"
        }, 404

    if reprint_type == "1":
        imprimir_registro(
            registro,
            solo_negocio=False,
            cantidad_copias=1
        )

        return {
            "message":
            "Reimpresas: copia del cliente y copia del negocio"
        }, 200

    elif reprint_type == "2":
        imprimir_solo_cliente(registro)

        return {
            "message":
            "Reimpresa: solo copia del cliente"
        }, 200

    elif reprint_type == "3":
        imprimir_registro(
            registro,
            solo_negocio=True,
            cantidad_copias=1
        )

        return {
            "message":
            "Reimpresa: solo copia del negocio"
        }, 200

    return {
        "error": "Tipo de reimpresión inválido"
    }, 400
    
    
def update_order(order_id, data, validar_datos_numericos):
    try:
        registro = Registro.query.get(order_id)

        if not registro:
            return ({"error": "Orden no encontrada"}), 404
        
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
                return ({"error": error_message}), 400
            
        # Actualizar campos con validaciones
        if "nombreCliente" in data:
            if len(data["nombreCliente"].strip()) < 3:
                return ({"error": "El nombre del cliente debe tener al menos 3 caracteres"}), 400
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
                return ({"error": "El número de celular debe tener exactamente 10 dígitos"}), 400
            registro.celular = data["celular"]
            
        if "telefono" in data:
            registro.telefono = data["telefono"]
            
        if "observaciones" in data:
            registro.observaciones = data["observaciones"]
            
        if "finalizada" in data:
            registro.finalizada = bool(data["finalizada"]) 
            
        db.session.commit()
        
        return ({"message": "Orden actualizada correctamente"}), 200
    except Exception:
        db.session.rollback()
        raise
    
    
def create_order(data, validar_datos_numericos):
    
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

    if not data or any(
        field not in data
        for field in required_fields
    ):
        return {
            "error": "Faltan datos requeridos"
        }, 400

    if len(data["nombreCliente"].strip()) < 3:
        return {
            "error":
            "El nombre del cliente debe tener al menos 3 caracteres"
        }, 400

    if not re.fullmatch(
        r"\d{10}",
        data["celular"]
    ):
        return {
            "error":
            "El número de celular debe tener 10 dígitos"
        }, 400

    valid, error_message = validar_datos_numericos(data)

    if not valid:
        return {
            "error": error_message
        }, 400

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
        return {
            "error":
            "Error en la codificación del texto"
        }, 400

    if len(observaciones) < 5:
        return {
            "error":
            "Las observaciones deben tener al menos 5 caracteres"
        }, 400

    if len(observaciones) > 500:
        return {
            "error":
            "Las observaciones no pueden exceder 500 caracteres"
        }, 400

    vendedor = Empleado.query.filter_by(
        codigo=data["vendedor"]
    ).first()

    if not vendedor:
        return {
            "error":
            "El código del vendedor no es válido"
        }, 404

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
            valorTotal=float(
                data["valorTotal"]
            ),
            abono=float(
                data["abono"]
            ),
            saldo=float(
                data["saldo"]
            ),
            celular=data["celular"],
            telefono=data.get(
                "telefono"
            ),
            observaciones=observaciones,
            vendedor=data["vendedor"].strip(),
            medioPago=data["medioPago"].strip()
        )

        db.session.add(
            nuevo_registro
        )

        db.session.flush()

        if nuevo_registro.id > (
            ultimo_id + 2
        ):
            db.session.rollback()

            db.session.execute(
                db.text(
                    f"DBCC CHECKIDENT("
                    f"'arreglos', "
                    f"RESEED, "
                    f"{ultimo_id})"
                )
            )

            db.session.commit()

            return {
                "error":
                (
                    "Secuencia de IDs corregida. "
                    "Reintente guardar."
                )
            }, 409

        cantidad_copias = max(
            1,
            int(
                data.get(
                    "cantidadObjetos",
                    1
                )
            )
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

        return {
            "message":
            "Datos guardados correctamente",
            "id":
            nuevo_registro.id
        }, 201

    except Exception:
        db.session.rollback()
        raise