from app import create_app
from app.models import Empleado
from app.database.db import db
from app.security.password_service import hash_password

app = create_app()

with app.app_context():

    empleados = Empleado.query.all()

    for empleado in empleados:

        # Evitar hashear dos veces
        if empleado.contrasena.startswith("$2"):
            continue

        empleado.contrasena = hash_password(
            empleado.contrasena
        )

        print(f"{empleado.codigo} actualizado")

    db.session.commit()

    print("Migración finalizada.")