from app.services.printing.escpos_commands import PRINTER_COMMANDS
from app.config.business_config import (
    BUSINESS_NAME,
    BUSINESS_BRANCH,
    OWNER_NAME,
    NIT,
    TAX_REGIME,
    ADDRESS,
    PHONE,
    WARNING_1,
    WARNING_2,
    WARNING_3
)

def construir_ticket_cliente(registro):
    # Formatos de fecha y valores
    fecha_entrega = registro.fechaEntrega.strftime('%d/%m/%Y %H:%M')
    fecha_creacion = registro.fechaCreacion.strftime('%d/%m/%Y %H:%M')
    valor = f"${float(registro.valorTotal):,.0f}".replace(",", ".")
    abono = f"${float(registro.abono):,.0f}".replace(",", ".")
    saldo = f"${float(registro.saldo):,.0f}".replace(",", ".")
    
    # Contenido para el cliente
    contenido_cliente = (
        f"{PRINTER_COMMANDS['INIT'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['FONT_LARGE'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['ALIGN_CENTER'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['BOLD_ON'].decode('latin-1')}"
        f"{BUSINESS_NAME}\n"
        f"{BUSINESS_BRANCH}\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['FONT_LARGE'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['BOLD_ON'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['FONT_NORMAL'].decode('latin-1')}" 
        f"{OWNER_NAME}\n"
        f"NIT {NIT} {TAX_REGIME}\n"
        f"{ADDRESS}\n"
        f"Telefono: {PHONE}\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['FONT_LARGE'].decode('latin-1')}" 
        f"ORDEN DE ARREGLO N: {registro.id}\n"
        f"Fecha: {fecha_creacion}\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['BOLD_OFF'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['FONT_NORMAL'].decode('latin-1')}"
        f"{'Cliente:':<12}{registro.nombreCliente}\n"
        f"{'Cel:':<12}{registro.celular}\n"
        f"{'Entrega:':<12}{fecha_entrega}\n"
        f"{'Valor:':<12}{valor}\n"
        f"{'Abono:':<12}{abono}\n"
        f"{'Saldo:':<12}{saldo}\n"
        f"{'Telefono adicional:':<12}{registro.telefono or 'N/A'}\n"
        f"Articulo para:\n{registro.observaciones}\n"
        f"\n{PRINTER_COMMANDS['FONT_NORMAL'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['BOLD_ON'].decode('latin-1')}"
        f"{WARNING_1}\n"
        f"{WARNING_2}\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1')}" 
        f"{WARNING_3}\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1') * 4}"
        f"{PRINTER_COMMANDS['CUT_PAPER'].decode('latin-1')}"
    )
    
    return contenido_cliente


def construir_ticket_negocio(registro):
    # Formatos de fecha y valores
    fecha_entrega = registro.fechaEntrega.strftime('%d/%m/%Y %H:%M')
    
    # Contenido para el negocio (compacto)
    contenido_negocio = (
        f"{PRINTER_COMMANDS['INIT'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['ALIGN_CENTER'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['BOLD_ON'].decode('latin-1')}"
        "====================\n"
        "COPIA INTERNA\n"
        f"{BUSINESS_NAME}\n"
        f"{BUSINESS_BRANCH}\n"
        "====================\n"
        f"{PRINTER_COMMANDS['BOLD_OFF'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['FONT_SMALL'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['ALIGN_CENTER'].decode('latin-1')}"
        f"ORDEN #:  {registro.id}\n"
        f"Cliente:  {registro.nombreCliente}\n"
        f"Entrega:  {fecha_entrega.split()[0]}  {fecha_entrega.split()[1]}\n"
        f"Celular:  {registro.celular}\n"
        f"Articulo para:\n  {registro.observaciones}\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1') * 4}"
        f"{PRINTER_COMMANDS['CUT_PAPER'].decode('latin-1')}"
    )
    
    return contenido_negocio