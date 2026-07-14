from app.models import Empleado
from app.database.db import db


def get_all():
    return Empleado.query.all()


def get_by_id(employee_id):
    return db.session.get(Empleado, employee_id)


def get_by_code(codigo):
    return Empleado.query.filter_by(
        codigo=codigo
    ).first()


def add(empleado):
    db.session.add(empleado)


def commit():
    db.session.commit()


def rollback():
    db.session.rollback()