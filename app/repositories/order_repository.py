from app.database.db import db
from app.models import Registro, Empleado


def get_all_orders():
    return Registro.query.order_by(
        Registro.fechaCreacion.desc()
    ).all()


def get_order_by_id(order_id):
    return db.session.get(Registro, order_id)


def get_employee_by_code(codigo):
    return Empleado.query.filter_by(
        codigo=codigo
    ).first()


def get_last_order_id():
    return db.session.execute(
        db.text(
            "SELECT ISNULL(MAX(id),0) FROM arreglos"
        )
    ).scalar()


def add_order(registro):
    db.session.add(registro)


def delete(registro):
    db.session.delete(registro)


def flush():
    db.session.flush()


def commit():
    db.session.commit()


def rollback():
    db.session.rollback()


def reseed_order_identity(last_id):
    db.session.execute(
        db.text(
            f"DBCC CHECKIDENT('arreglos', RESEED, {last_id})"
        )
    )