from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from PIL import Image
import os, re, win32print, win32api
from datetime import datetime
import time
import logging
import unicodedata

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
    'CUT_PAPER': b'\x1D\x56\x42\x00',    # Cortar papel
    'LINE_FEED': b'\x0A',            # Salto de línea
}

# 1. Configuración de la aplicación
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Configuración de la base de datos
SERVER = 'localhost\\SQLEXPRESS'
DATABASE = 'ElImperioDeLosBolsosBelen'
DRIVER = 'ODBC Driver 17 for SQL Server'
USERNAME = os.getenv('SQL_USER', 'sa')
PASSWORD = os.getenv('SQL_PASSWORD', '1234')

app.config["SQLALCHEMY_DATABASE_URI"] = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}&TrustServerCertificate=yes&charset=utf8"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 3. Inicialización de SQLAlchemy
db = SQLAlchemy(app)

# 4. Definición del modelo
class Empleado(db.Model):
    __tablename__ = 'empleados'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(16), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    administrador = db.Column(db.Boolean, default=False, nullable=False)

class Registro(db.Model):
    __tablename__ = 'arreglos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreCliente = db.Column(db.String(100), nullable=False)
    fechaEntrega = db.Column(db.DateTime, nullable=False)
    fechaCreacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valorTotal = db.Column(db.Numeric(10, 2), nullable=False)
    abono = db.Column(db.Numeric(10, 2), nullable=False)
    saldo = db.Column(db.Numeric(10, 2), nullable=False)
    celular = db.Column(db.String(10), nullable=False)
    telefono = db.Column(db.String(16), nullable=True)
    # Usar UnicodeText en lugar de String para manejar mejor los caracteres especiales
    observaciones = db.Column(db.UnicodeText(500), nullable=False)
    vendedor = db.Column(db.String(50), nullable=False)
    finalizada = db.Column(db.Boolean, default=False, nullable=False) 
    medioPago = db.Column(db.String(20), nullable=False, default='efectivo')

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

def verificar_configuracion_db():
    """Verifica que la configuración de la base de datos sea correcta para UTF-8"""
    try:
        with app.app_context():
            # Verificar la codificación de la columna observaciones
            result = db.session.execute(db.text("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    COLLATION_NAME
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'arreglos' AND COLUMN_NAME = 'observaciones'
            """)).fetchone()
            
            if result:
                print(f"Configuración columna observaciones:")
                print(f"  Tipo: {result[1]}")
                print(f"  Longitud: {result[2]}")
                print(f"  Collation: {result[3]}")
                
                if result[1] == 'varchar':
                    print("⚠️  ADVERTENCIA: La columna es VARCHAR, considera cambiar a NVARCHAR para mejor soporte Unicode")
                    print("   Ejecuta: ALTER TABLE arreglos ALTER COLUMN observaciones NVARCHAR(500)")
            else:
                print("❌ No se pudo verificar la configuración de la columna observaciones")
    except Exception as e:
        print(f"Error al verificar configuración DB: {e}")

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

# Comando de la imagen en una variable global
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

# 6. Rutas de la API
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    required_fields = ["codigo", "contrasena"]

    # Validar que los campos requeridos estén presentes
    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "Faltan datos requeridos"}), 400

    # Buscar el empleado por código
    empleado = Empleado.query.filter_by(codigo=data["codigo"].strip()).first()

    if not empleado:
        return jsonify({"error": "El código de usuario no es válido"}), 404

    # Validar la contraseña
    if empleado.contrasena != data["contrasena"].strip():
        return jsonify({"error": "La contraseña es incorrecta"}), 401

    # Si las credenciales son correctas, devolver los datos del usuario
    return jsonify({
        "message": "Inicio de sesión exitoso",
        "nombre": empleado.nombre,
        "codigo": empleado.codigo,
        "administrador": empleado.administrador
    }), 200

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
    
@app.route("/getAllEmployees", methods=["GET"])
def obtener_empleados():
    try:
        empleados = Empleado.query.all()
        return jsonify([
            {
                "codigo": emp.codigo,
                "nombre": emp.nombre
            } for emp in empleados
        ]), 200
    except Exception as e:
        return jsonify({"error": f"Error al obtener empleados: {str(e)}"}), 500

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

# 7. Inicialización de la base de datos
with app.app_context():
    try:
        db.engine.connect()
        print("✅ Conexión exitosa a SQL Server")
        db.create_all()
        print("✅ Base de datos 'ElImperioDeLosBolsoBelen' verificada")
        print("✅ Tabla 'arreglos' lista para usar")
        
        # Verificar configuración
        verificar_configuracion_db()
        
        admin_empleado = Empleado.query.filter_by(codigo="ADMIN").first()
        if not admin_empleado:
            nuevo_admin = Empleado(
                nombre="ADMINISTRADOR",
                telefono="0000000000",
                codigo="ADMIN",
                contrasena="0000",
                administrador=True
            )
            db.session.add(nuevo_admin)
            db.session.commit()
            print("✅ Empleado administrador creado por defecto")
        print("\n📊 Sistema listo para recibir datos")
    except Exception as e:
        print("\n❌ Error de inicialización:")
        if "Login failed" in str(e):
            print("  → Credenciales SQL Server incorrectas")
        elif "Cannot open database" in str(e):
            print("  → La base de datos no existe")
        elif "Server is not found" in str(e):
            print("  → SQL Server no está corriendo")
        else:
            print(f"  → {str(e)}")
        print("\n💡 Verifica:")
        print("  1. Que SQL Server esté corriendo")
        print("  2. Las credenciales de SQL Server")
        print("  3. Que la base de datos 'ElImperioDeLosBolsoBelen' exista")
        raise e

# 8. Punto de entrada de la aplicación
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)