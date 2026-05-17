from app.database.db import db
from app.models import Empleado

def initialize_database():
    try:
        db.engine.connect()
        print("Conexión a la base de datos establecida exitosamente.")
        db.create_all()
        print("Base de datos verificada")
        print("Tablas listas")
        admin = Empleado.query.filter_by(codigo="ADMIN").first()
        if not admin:
            nuevo_admin = Empleado(
                nombre="Administrador",
                telefono="0000000000",
                codigo="ADMIN",
                contrasena="0000",
                administrador=True
            )
            
            db.session.add(nuevo_admin)
            db.session.commit()
            print("Usuario administrador creado exitosamente.")
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"Error inicializando la base de datos: {e}")
        raise