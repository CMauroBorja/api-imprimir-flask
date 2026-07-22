import time

from app.config.logging_config import logger

from app.services.printing.windows_printer import (
    enviar_a_impresora
)

from app.services.printing.ticket_builder import (
    construir_ticket_cliente,
    construir_ticket_negocio
)


def imprimir_registro(
    registro,
    solo_negocio=False,
    cantidad_copias=1
):
    """Imprime tickets ESC/POS - impresora térmica DIG-E200I"""

    contenido_cliente = construir_ticket_cliente(
        registro
    )

    contenido_negocio = construir_ticket_negocio(
        registro
    )

    logger.info(
        f"Iniciando impresión de la orden {registro.id}"
    )

    try:

        # Primero imprimir la copia del cliente
        if not solo_negocio:

            enviar_a_impresora(
                contenido_cliente,
                "Ticket Cliente"
            )

            logger.info(
                f"Ticket del cliente impreso. Orden: {registro.id}"
            )

            time.sleep(0.5)

        # Luego imprimir las copias del negocio
        for i in range(cantidad_copias):

            enviar_a_impresora(
                contenido_negocio,
                "Ticket Negocio"
            )

            logger.info(
                f"Ticket del negocio impreso ({i + 1}/{cantidad_copias}). "
                f"Orden: {registro.id}"
            )

            if i < cantidad_copias - 1:
                time.sleep(0.5)

        logger.info(
            f"Impresión finalizada correctamente. Orden: {registro.id}"
        )

    except Exception as e:

        logger.exception(
            f"Error al imprimir la orden {registro.id}"
        )

        raise RuntimeError(
            f"Error al imprimir: {e}"
        ) from e


def imprimir_solo_cliente(registro):
    """Imprime únicamente la copia del cliente."""

    contenido_cliente = construir_ticket_cliente(
        registro
    )

    try:

        enviar_a_impresora(
            contenido_cliente,
            "Ticket Cliente"
        )

        logger.info(
            f"Reimpresión del ticket del cliente. Orden: {registro.id}"
        )

    except Exception as e:

        logger.exception(
            f"Error al imprimir el ticket del cliente. Orden: {registro.id}"
        )

        raise RuntimeError(
            f"Error al imprimir ticket del cliente: {e}"
        ) from e