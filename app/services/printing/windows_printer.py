import win32print

def enviar_a_impresora(contenido_escpos, nombre_documento="Ticket"):
    printer_name = win32print.GetDefaultPrinter()
    hPrinter = win32print.OpenPrinter(printer_name)

    try:
        win32print.StartDocPrinter(
            hPrinter,
            1,
            (nombre_documento, None, "RAW")
        )

        win32print.StartPagePrinter(hPrinter)

        win32print.WritePrinter(
            hPrinter,
            contenido_escpos.encode("latin-1")
        )

        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)

    finally:
        win32print.ClosePrinter(hPrinter)