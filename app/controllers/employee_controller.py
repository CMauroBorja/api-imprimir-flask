from flask import Blueprint, jsonify
from app.models import Empleado

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