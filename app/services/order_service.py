from datetime import datetime
from app.config.logging_config import logger
from app.models import Registro, Abono
from app.serializers import serialize_order_list, serialize_order
from app.repositories import order_repository

from app.services.printing.printer_service import (
    imprimir_registro,
    imprimir_solo_cliente
)

from app.validators.order_validator import (
    validar_celular,
    validar_datos_numericos,
    validar_nombre_cliente,
    validar_observaciones
)

from app.exceptions.custom_exceptions import (
    ConflictError,
    ValidationError,
    NotFoundError,
    PrinterError
)

def get_all_orders():
    registros = order_repository.get_all()
    
    return serialize_order_list(registros), 200


def get_order_by_id(order_id):
    
    registro = order_repository.get_by_id(
        order_id
    )

    if not registro:
        raise NotFoundError(
            "Orden no encontrada"
        )

    if registro.finalizada:
        raise ValidationError(
            "Esta orden ya fue finalizada"
        )

    return serialize_order(
        registro
    ), 200
    

def delete_order_by_id(order_id):
    
    registro = order_repository.get_by_id(
        order_id
    )

    if not registro:
        raise NotFoundError(
            "Orden no encontrada"
        )

    try:

        order_repository.delete(
            registro
        )

        order_repository.commit()

    except Exception:

        order_repository.rollback()
        raise

    logger.info(
        f"Orden {order_id} eliminada"
    )

    return {
        "message": "Orden eliminada correctamente"
    }, 200
    
    
def reprint_order_by_id(order_id, reprint_type):
    registro = order_repository.get_by_id(order_id)

    if not registro:

        raise NotFoundError(
            "Orden no encontrada"
        )

    if reprint_type == "1":
        
        imprimir_registro(
            registro,
            solo_negocio=False,
            cantidad_copias=1
        )

        mensaje = "Reimpresas: copia del cliente y copia del negocio"

    elif reprint_type == "2":
        
        imprimir_solo_cliente(registro)

        mensaje = "Reimpresa: solo copia del cliente"

    elif reprint_type == "3":
        
        imprimir_registro(
            registro,
            solo_negocio=True,
            cantidad_copias=1
        )
    
        mensaje = "Reimpresa: solo copia del negocio"
    
    else:
        
        raise ValidationError(
            "Tipo de reimpresión inválido")
        
    logger.info(
        f"Orden {order_id} reimpresa. Tipo: {reprint_type}"
    )
    
    return {
        "message": mensaje
    }, 200


def update_order(order_id, data):
    
    registro = order_repository.get_by_id(
        order_id
    )

    if not registro:
        raise NotFoundError(
            "Orden no encontrada"
        )

    # Validar datos numéricos
    if any(
        key in data
        for key in [
            "valorTotal",
            "abono",
            "saldo"
        ]
    ):
        valores = {
            "valorTotal": float(
                data.get(
                    "valorTotal",
                    registro.valorTotal
                )
            ),
            "abono": float(
                data.get(
                    "abono",
                    registro.abono
                )
            ),
            "saldo": float(
                data.get(
                    "saldo",
                    registro.saldo
                )
            )
        }

        valid, error_message = validar_datos_numericos(
            valores
        )

        if not valid:
            raise ValidationError(
                error_message
            )

    if "nombreCliente" in data:

        if not validar_nombre_cliente(
            data["nombreCliente"]
        ):
            raise ValidationError(
                "El nombre del cliente debe tener al menos 3 caracteres"
            )

        registro.nombreCliente = (
            data["nombreCliente"].strip()
        )

    if "fechaEntrega" in data:
        registro.fechaEntrega = (
            datetime.strptime(
                data["fechaEntrega"],
                "%Y-%m-%d %H:%M"
            )
        )

    if "valorTotal" in data:
        registro.valorTotal = float(
            data["valorTotal"]
        )

    if "abono" in data:
        
        abono_anterior = float(
            registro.abono
        )

        nuevo_abono_total = float(
            data["abono"]
        )

        diferencia_abono = (
            nuevo_abono_total
            - abono_anterior
        )

        registro.abono = nuevo_abono_total

        if diferencia_abono > 0:

            nuevo_abono = Abono(
                orden_id=registro.id,
                valor=diferencia_abono
            )

            order_repository.add(
                nuevo_abono
            )

    if "saldo" in data:
        registro.saldo = float(
            data["saldo"]
        )

    if "celular" in data:

        if not validar_celular(
            data["celular"]
        ):
            raise ValidationError(
                "El número de celular debe tener exactamente 10 dígitos"
            )

        registro.celular = data["celular"]

    if "telefono" in data:
        registro.telefono = data["telefono"]

    if "observaciones" in data:

        if not validar_observaciones(
            data["observaciones"]
        ):
            raise ValidationError(
                "Las observaciones no cumplen con los requisitos"
            )

        registro.observaciones = (
            data["observaciones"]
        )

        if "finalizada" in data:
            
            nueva_finalizada = bool(
                data["finalizada"]
            )

            if nueva_finalizada and not registro.finalizada:

                saldo_actual = float(
                    data.get(
                        "saldo",
                        registro.saldo
                    )
                )

                if abs(saldo_actual) > 0.01:
                    raise ValidationError(
                        "No se puede finalizar la orden. "
                        "La orden debe estar totalmente pagada."
                    )

                registro.finalizada = True

                registro.fechaFinalizacion = (
                    datetime.now()
                )

            elif not nueva_finalizada and registro.finalizada:

                raise ValidationError(
                    "Esta orden ya fue finalizada "
                    "y no puede volver a abrirse."
                )

    try:

        order_repository.commit()

    except Exception:

        order_repository.rollback()
        raise

    logger.info(
        f"Orden {order_id} actualizada"
    )

    return {
        "message": "Orden actualizada correctamente"
    }, 200
    
    
def create_order(data):
    
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
        raise ValidationError(
            "Faltan campos requeridos"
        )

    if not validar_nombre_cliente(
        data["nombreCliente"]
    ):
        raise ValidationError(
            "El nombre del cliente debe tener al menos 3 caracteres"
        )

    if not validar_celular(
        data["celular"]
    ):
        raise ValidationError(
            "El número de celular debe tener 10 dígitos"
        )

    if not validar_observaciones(
        data["observaciones"]
    ):
        raise ValidationError(
            "Las observaciones no cumplen con los requisitos"
        )

    valid, error_message = validar_datos_numericos(
        data
    )

    if not valid:
        raise ValidationError(
            error_message
        )

    observaciones_raw = data["observaciones"]

    if isinstance(
        observaciones_raw,
        str
    ):
        observaciones_clean = (
            observaciones_raw.strip()
        )
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
        raise ValidationError(
            "Error en la codificación del texto"
        )

    if len(observaciones) < 5:
        raise ValidationError(
            "Las observaciones deben tener al menos 5 caracteres"
        )

    if len(observaciones) > 500:
        raise ValidationError(
            "Las observaciones no pueden exceder 500 caracteres"
        )

    vendedor = order_repository.get_employee_by_code(
        data["vendedor"]
    )

    if not vendedor:
        raise NotFoundError(
            "El código del vendedor no es válido"
        )

    ultimo_id = order_repository.get_last_order_id()

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
        telefono=data.get("telefono"),
        observaciones=observaciones,
        vendedor=data["vendedor"].strip(),
        medioPago=data["medioPago"].strip()
    )

    try:

        order_repository.add(
            nuevo_registro
        )

        order_repository.flush()

        if nuevo_registro.id > (
            ultimo_id + 2
        ):
            order_repository.rollback()

            order_repository.reseed_order_identity(
                ultimo_id
            )

            order_repository.commit()

            raise ConflictError(
                "Secuencia de IDs corregida. Reintente guardar."
            )
            
        abono_inicial = float(data["abono"])
        
        if abono_inicial > 0:
            nuevo_abono = Abono(
                orden_id=nuevo_registro.id,
                valor=abono_inicial
            )

            order_repository.add(
                nuevo_abono
            )

        order_repository.commit()

    except ConflictError:
        raise

    except Exception:

        order_repository.rollback()
        raise

    cantidad_copias = max(
        1,
        int(
            data.get(
                "cantidadObjetos",
                1
            )
        )
    )

    try:

        imprimir_registro(
            nuevo_registro,
            solo_negocio=data.get(
                "tieneWhatsapp",
                False
            ),
            cantidad_copias=cantidad_copias
        )

    except PrinterError:

        logger.error(
            f"Orden {nuevo_registro.id} "
            f"creada pero no pudo imprimirse"
        )

        return {
            "message": (
                "Orden creada, pero no fue posible imprimirla"
            ),
            "id": nuevo_registro.id,
            "impresion": False
        }, 201

    logger.info(
        f"Orden {nuevo_registro.id} creada "
        f"por el vendedor {nuevo_registro.vendedor}"
    )

    return {
        "message": "Datos guardados correctamente",
        "id": nuevo_registro.id,
        "impresion": True
    }, 201
    

def finalize_order(order_id, data):
    
    registro = order_repository.get_by_id(
        order_id
    )

    if not registro:
        raise NotFoundError(
            "Orden no encontrada"
        )

    if registro.finalizada:
        raise ValidationError(
            "Esta orden ya fue finalizada"
        )

    saldo_actual = float(
        registro.saldo
    )

    abono_final = float(
        data.get(
            "abonoFinal",
            0
        )
    )

    if saldo_actual > 0:

        if abono_final <= 0:
            raise ValidationError(
                "Debe ingresar el abono final."
            )

        if abs(
            abono_final - saldo_actual
        ) > 0.01:
            raise ValidationError(
                "El abono final debe ser igual "
                "al saldo pendiente."
            )

    else:

        abono_final = 0

    try:

        if abono_final > 0:

            nuevo_abono = Abono(
                orden_id=registro.id,
                valor=abono_final
            )

            order_repository.add(
                nuevo_abono
            )

            registro.abono = (
                float(registro.abono)
                + abono_final
            )

            registro.saldo = 0

        registro.finalizada = True

        registro.fechaFinalizacion = (
            datetime.now()
        )

        order_repository.commit()

    except Exception:

        order_repository.rollback()
        raise

    logger.info(
        f"Orden {order_id} finalizada"
    )

    return {
        "message": "Orden finalizada correctamente",
        "id": registro.id
    }, 200