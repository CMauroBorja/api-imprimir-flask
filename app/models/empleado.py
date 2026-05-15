from app.database.db import db

class Empleado(db.Model):
    __tablename__ = 'empleados'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(16), nullable=False)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    administrador = db.Column(db.Boolean, default=False, nullable=False)