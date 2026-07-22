import win32print

from app.config.logging_config import logger


def enviar_a_impresora(
    contenido_escpos,
    nombre_documento="Ticket"
):

    printer_name = win32print.GetDefaultPrinter()

    logger.info(
        f"Impresora seleccionada: {printer_name}"
    )

    hPrinter = win32print.OpenPrinter(
        printer_name
    )

    try:

        logger.info(
            f"Enviando documento '{nombre_documento}' a la impresora"
        )

        win32print.StartDocPrinter(
            hPrinter,
            1,
            (
                nombre_documento,
                None,
                "RAW"
            )
        )

        win32print.StartPagePrinter(
            hPrinter
        )

        win32print.WritePrinter(
            hPrinter,
            contenido_escpos.encode(
                "latin-1"
            )
        )

        win32print.EndPagePrinter(
            hPrinter
        )

        win32print.EndDocPrinter(
            hPrinter
        )

        logger.info(
            f"Documento '{nombre_documento}' enviado correctamente"
        )

    finally:

        win32print.ClosePrinter(
            hPrinter
        )

        logger.info(
            "Conexión con la impresora cerrada"
        )