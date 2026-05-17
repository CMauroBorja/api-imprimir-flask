import os
import time
import win32print
from PIL import Image
from app.models import Registro

def convertir_imagen_a_escpos(ruta_imagen, ancho=384):
    """Convierte una imagen a formato ESC/POS"""
    img = Image.open(ruta_imagen)
    # Redimensionar manteniendo proporción
    ratio = ancho / float(img.size[0])
    alto = int((float(img.size[1]) * float(ratio)))
    img = img.resize((ancho, alto), Image.Resampling.LANCZOS)
    # Convertir a blanco y negro
    img = img.convert('1')
    
    # Convertir imagen a bytes ESC/POS
    width_bytes = int(ancho / 8)
    dots = []
    for y in range(alto):
        dots.extend(img.tobytes()[y * width_bytes:(y + 1) * width_bytes])
    
    # Comando ESC/POS para imprimir imagen
    comando = b'\x1D\x76\x30\x00'
    comando += bytes([width_bytes & 0xff])
    comando += bytes([width_bytes >> 8])
    comando += bytes([alto & 0xff])
    comando += bytes([alto >> 8])
    comando += bytes(dots)
    
    return comando

def imprimir_registro(registro, solo_negocio=False, cantidad_copias=1):
    """Imprime tickets ESC/POS directamente en impresora térmica DIG-E200I"""
    
    def enviar_a_impresora(contenido_escpos):
        """Envía comandos ESC/POS directamente a la impresora predeterminada"""
        printer_name = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, contenido_escpos.encode("latin-1"))
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

    # Formatos de fecha y valores
    fecha_entrega = registro.fechaEntrega.strftime('%d/%m/%Y %H:%M')
    fecha_creacion = registro.fechaCreacion.strftime('%d/%m/%Y %H:%M')
    valor = f"${float(registro.valorTotal):,.0f}".replace(",", ".")
    abono = f"${float(registro.abono):,.0f}".replace(",", ".")
    saldo = f"${float(registro.saldo):,.0f}".replace(",", ".")

    # Contenido para el negocio (compacto)
    contenido_negocio = (
        f"{PRINTER_COMMANDS['INIT'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['ALIGN_CENTER'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['BOLD_ON'].decode('latin-1')}"
        "====================\n"
        "COPIA INTERNA\n"
        "NEGOCIO\n"
        "BELEN\n"
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

    # Contenido para el cliente
    contenido_cliente = (
        f"{PRINTER_COMMANDS['INIT'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['FONT_LARGE'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['ALIGN_CENTER'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['BOLD_ON'].decode('latin-1')}"
        "EL IMPERIO DE LOS BOLSOS\n" 
        "BELEN\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['FONT_LARGE'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['BOLD_ON'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['FONT_NORMAL'].decode('latin-1')}" 
        "Carmen Teresa Bustamante Rua\n"
        "NIT 21945345-8 Regimen Simplificado\n"
        "CR 76 # 32 - 105 BELEN\n"
        "Telefono: 3005665208\n"
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
        "* PASADOS 30 DIAS \n"
        " NO SE RESPONDE POR ARTICULO *\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1')}" 
        "* NO SE HACE DEVOLICION DE DINERO *\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1') * 4}"
        f"{PRINTER_COMMANDS['CUT_PAPER'].decode('latin-1')}"
    )

    contenidos = [contenido_negocio] if solo_negocio else [contenido_cliente, contenido_negocio]

    try:
        # Primero imprimir la copia del cliente (si aplica)
        if not solo_negocio:
            enviar_a_impresora(contenido_cliente)
            time.sleep(0.5)

        # Luego imprimir las copias del negocio según cantidad_copias
        for i in range(cantidad_copias):
            enviar_a_impresora(contenido_negocio)
            if i < cantidad_copias - 1:  # No esperar después de la última impresión
                time.sleep(0.5)
    except Exception as e:
        raise RuntimeError(f"Error al imprimir: {e}") from e
        
def imprimir_solo_cliente(registro):
    """Imprime solo el ticket del cliente"""
    def enviar_a_impresora(contenido_escpos):
        """Envía comandos ESC/POS directamente a la impresora predeterminada"""
        printer_name = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(printer_name)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket Cliente", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, contenido_escpos.encode("latin-1"))
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)

    # Formatos de fecha y valores
    fecha_entrega = registro.fechaEntrega.strftime('%d/%m/%Y %H:%M')
    fecha_creacion = registro.fechaCreacion.strftime('%d/%m/%Y %H:%M')
    valor = f"${float(registro.valorTotal):,.0f}".replace(",", ".")
    abono = f"${float(registro.abono):,.0f}".replace(",", ".")
    saldo = f"${float(registro.saldo):,.0f}".replace(",", ".")

    # Contenido solo para el cliente
    contenido_cliente = (
        f"{PRINTER_COMMANDS['INIT'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['FONT_LARGE'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['ALIGN_CENTER'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['BOLD_ON'].decode('latin-1')}"
        "EL IMPERIO DE LOS BOLSOS\n" 
        "BELEN\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['FONT_LARGE'].decode('latin-1')}" 
        f"{PRINTER_COMMANDS['BOLD_ON'].decode('latin-1')}"
        f"{PRINTER_COMMANDS['FONT_NORMAL'].decode('latin-1')}" 
        "Jirlesa Maria Agudelo Correa\n"
        "NIT 1152445775 Regimen Simplificado\n"
        "CLL 46 N 49-01 BELEN\n"
        "Telefono: 3506878318 - 3106503062\n"
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
        "* PASADOS 30 DIAS \n"
        " NO SE RESPONDE POR ARTICULO *\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1')}" 
        "* NO SE HACE DEVOLICION DE DINERO *\n"
        f"{PRINTER_COMMANDS['LINE_FEED'].decode('latin-1') * 4}"
        f"{PRINTER_COMMANDS['CUT_PAPER'].decode('latin-1')}"
    )

    try:
        enviar_a_impresora(contenido_cliente)
    except Exception as e:
        raise RuntimeError(f"Error al imprimir ticket del cliente: {e}") from e
    
PRINTER_COMMANDS = {
    'INIT': b'\x1B\x40',           # Inicializar impresora
    'ALIGN_LEFT': b'\x1B\x61\x00', # Alineación izquierda
    'ALIGN_CENTER': b'\x1B\x61\x01', # Alineación centro
    'ALIGN_RIGHT': b'\x1B\x61\x02',  # Alineación derecha
    'FONT_SMALL': b'\x1B\x21\x01',   # Fuente pequeña
    'FONT_NORMAL': b'\x1B\x21\x00',  # Fuente normal
    'FONT_LARGE': b'\x1B\x21\x10',   # Fuente grande
    'FONT_EXTRA_LARGE': b'\x1B\x21\x20', # Fuente extra grande
    'BOLD_ON': b'\x1B\x45\x01',      # Negrita activada
    'BOLD_OFF': b'\x1B\x45\x00',     # Negrita desactivada
    'LINE_FEED': b'\n',             # Salto de línea
    'CUT_PAPER': b'\x1D\x56\x42\x00',    # Cortar papel
}
 
try:
    LOGO_COMANDO = convertir_imagen_a_escpos('img/logoImperio.png')
except Exception as e:
    print(f"⚠️ Error al cargar el logo: {e}")
    print("➡️ Usando formato texto para el encabezado")
    LOGO_COMANDO = """
    ========================
        EL IMPERIO DE
    LOS BOLSOS BELEN
    ========================
    """
