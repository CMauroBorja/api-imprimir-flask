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