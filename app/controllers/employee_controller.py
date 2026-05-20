from flask import Blueprint, jsonify, request
from app.models import Empleado
from app.database.db import db

employee_bp = Blueprint("employees", __name__)

@employee_bp.route("/getAllEmployees", methods=["GET"])
def get_all_employees():
    empleados = Empleado.query.all()
    
    return jsonify([
        {
            "id": e.id,
            "nombre": e.nombre,
            "telefono": e.telefono,
            "codigo": e.codigo,
            "administrador": e.administrador
        }
        for e in empleados
    ])
    
@employee_bp.route("/createEmployee", methods=["POST"])
def create_employee():
    data = request.json
    
    required_fields = [
        "nombre",
        "telefono",
        "codigo",
        "contrasena",
        "administrador"
    ]
    
    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    empleado_existente = Empleado.query.filter_by(
        codigo=data["codigo"].strip()
    ).first()
    
    if empleado_existente:
        return jsonify({"error": "El codigo de usuario ya existe"}), 409
    
    nuevo = Empleado(
        nombre=data["nombre"].strip(),
        telefono=data["telefono"].strip(),
        codigo=data["codigo"].strip(),
        contrasena=data["contrasena"].strip(),
        administrador=data["administrador"]
    )
    
    db.session.add(nuevo)
    db.session.commit()
    
    return jsonify({"message": "Empleado creado exitosamente"}), 201