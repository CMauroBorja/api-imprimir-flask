# API Imprimir Flask

Backend desarrollado en Python y Flask para la gestión de órdenes, empleados e impresión de tickets térmicos mediante impresoras compatibles con ESC/POS.

---

# Estado del Proyecto

Proyecto en producción utilizado para la gestión de órdenes de servicio e impresión de comprobantes en establecimientos comerciales.

Actualmente se encuentra refactorizado bajo una arquitectura modular basada en:

* Controllers
* Models
* Services
* Validators
* Config
* Bootstrap

La lógica que anteriormente se encontraba centralizada fue distribuida en componentes especializados para facilitar mantenimiento, escalabilidad y futuras mejoras.

---

# Tecnologías Utilizadas

* Python 3.14
* Flask
* Flask-CORS
* SQLAlchemy
* SQL Server
* PyODBC
* PyWin32
* ESC/POS
* Git

---

# Arquitectura Actual

## Mapa General

```text
run.py
  ↓
app/__init__.py
  ├─ config/
  │   ├─ settings.py
  │   └─ business_config.py
  │
  ├─ database/
  │   └─ db.py
  │
  ├─ bootstrap/
  │   └─ startup.py
  │
  ├─ models/
  │   ├─ empleado.py
  │   └─ registro.py
  │
  ├─ controllers/
  │   ├─ auth_controller.py
  │   ├─ employee_controller.py
  │   ├─ order_controller.py
  │   └─ print_controller.py
  │
  ├─ services/
  │   └─ printing/
  │       ├─ printer_service.py
  │       ├─ windows_printer.py
  │       ├─ ticket_builder.py
  │       └─ escpos_commands.py
  │
  └─ validators/
      ├─ employee_validator.py
      └─ order_validator.py
```

---

# Componentes del Sistema

## 1. Punto de Entrada

### run.py

Responsable de iniciar la aplicación Flask.

Funciones:

* Invoca `create_app()`
* Levanta el servidor Flask
* Escucha en `0.0.0.0:8080`

---

## 2. Factory de Flask

### app/__init__.py

Responsable de construir la aplicación.

Funciones:

* Crear instancia Flask
* Cargar configuración
* Inicializar CORS
* Inicializar SQLAlchemy
* Registrar Blueprints
* Inicializar la base de datos

Blueprints registrados:

* auth_bp
* employee_bp
* order_bp
* print_bp

---

## 3. Configuración

### settings.py

Configuración de conexión a SQL Server.

Variables:

* SERVER
* DATABASE
* DRIVER
* USERNAME
* PASSWORD

Construye:

```python
SQLALCHEMY_DATABASE_URI
```

---

### business_config.py

Contiene la configuración de negocio utilizada durante la impresión:

* Nombre del negocio
* Sucursal
* Propietario
* NIT
* Dirección
* Teléfono
* Mensajes y advertencias impresas

---

## 4. Base de Datos

### db.py

Expone la instancia principal:

```python
db = SQLAlchemy()
```

---

### startup.py

Se ejecuta al iniciar la aplicación.

Funciones:

* Verificar conexión
* Crear tablas
* Insertar usuario administrador inicial
* Validar estructura mínima del sistema

---

## 5. Modelos

### empleado.py

Tabla:

```text
empleados
```

Campos:

* id
* nombre
* telefono
* codigo
* contrasena
* administrador

---

### registro.py

Tabla:

```text
arreglos
```

Campos:

* id
* nombreCliente
* fechaEntrega
* fechaCreacion
* valorTotal
* abono
* saldo
* celular
* telefono
* observaciones
* vendedor
* finalizada
* medioPago

---

## 6. Controladores

### auth_controller.py

Endpoints:

```http
POST /login
```

Responsable de autenticación de usuarios.

---

### employee_controller.py

Endpoints:

```http
GET  /getAllEmployees
GET  /getEmployee/<employee_id>
POST /createEmployee
PUT  /updateEmployee/<codigo>
```

Responsable de la gestión de empleados.

---

### order_controller.py

Endpoints:

```http
GET    /getOrders
POST   /submitData
POST   /reprintOrder/<id>
PUT    /updateOrder/<id>
DELETE /deleteOrder/<id>
```

Responsable de:

* Creación de órdenes
* Consulta de órdenes
* Actualización
* Eliminación
* Reimpresión

---

### print_controller.py

Endpoints:

```http
GET /test-print/<registro_id>
```

Utilizado para pruebas de impresión.

---

## 7. Servicios de Impresión

### printer_service.py

Orquesta el proceso completo de impresión.

Funciones:

* imprimir_registro()
* imprimir_solo_cliente()

---

### windows_printer.py

Responsable de la comunicación con Windows.

Funciones:

* Obtener impresora predeterminada
* Enviar comandos RAW mediante win32print

---

### ticket_builder.py

Construye el contenido de los tickets.

Responsable de:

* Ticket cliente
* Ticket negocio
* Formato de fechas
* Formato monetario
* Aplicación de comandos ESC/POS

---

### escpos_commands.py

Centraliza los comandos ESC/POS reutilizables:

* Inicialización
* Negrilla
* Alineación
* Tamaños de fuente
* Saltos de línea
* Corte de papel

---

## 8. Validadores

### employee_validator.py

Reservado para futuras validaciones de empleados.

Actualmente sin uso.

---

### order_validator.py

Reservado para futuras validaciones de órdenes.

Actualmente sin uso.

---

# Flujo General del Sistema

```text
run.py
    ↓
create_app()
    ↓
Inicialización DB
    ↓
Registro Blueprints
    ↓
Consumo de Endpoints
    ↓
Controladores
    ↓
Modelos SQLAlchemy
    ↓
SQL Server
```

Flujo de creación de órdenes:

```text
POST /submitData
        ↓
order_controller
        ↓
Validaciones
        ↓
Registro SQL Server
        ↓
printer_service
        ↓
ticket_builder
        ↓
windows_printer
        ↓
Impresora térmica
```

---

# Instalación

Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

# Ejecución

```bash
python run.py
```

Servidor:

```text
http://localhost:8080
```

---

# Frontend Relacionado

Repositorio Frontend:

https://github.com/CMauroBorja/app-web-ordenes

---

# Próximas Mejoras

* Implementar validadores reutilizables.
* Incorporar variables de entorno (.env).
* Agregar pruebas unitarias.
* Implementar ejecución como servicio de Windows.
* Agregar sistema de logs centralizado.
* Mejorar manejo de errores y auditoría.