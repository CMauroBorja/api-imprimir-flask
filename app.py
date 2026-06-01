from flask import request, jsonify
from datetime import datetime
import os, re, time, logging, unicodedata
import win32print

from app.database.db import db
from app.models import Empleado, Registro
from app.services.printer_service import (
    imprimir_registro,
    imprimir_solo_cliente
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)