from flask import Blueprint, request, jsonify
from app.models import Empleado

auth_ph = Blueprint('auth', __name__)

@auth_ph.route('/login', methods=['POST'])
def login():
    data = request.json
    required_fields = ['codigo', 'contrasena']
    
    if not data or any(field not in data for field in required_fields):
        return jsonify({'error': 'Faltan datos requeridos'}), 400
    
    empleado = Empleado.query.filter_by(
        codigo=data['codigo'].strip()
    ).first()
    
    if not empleado:
        return jsonify({'error': 'El codigo de usuario no es valido'}), 404
    
    if empleado.contrasena != data['contrasena'].strip():
        return jsonify({'error': 'La contraseña es incorrecta'}), 401
    
    return jsonify ({
        'message': 'Inicio de sesión exitoso',
        'nombre': empleado.nombre,
        'codigo': empleado.codigo,
        'administrador': empleado.administrador
    }), 200