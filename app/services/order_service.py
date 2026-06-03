from app.models import Registro, Empleado
from app.database.db import db


def get_all_orders():
    registros = Registro.query.order_by(
        Registro.fechaCreacion.desc()
    ).all()

    return [
        {
            "id": r.id,
            "nombreCliente": r.nombreCliente,
            "fechaEntrega": r.fechaEntrega.strftime("%Y-%m-%d %H:%M"),
            "fechaCreacion": r.fechaCreacion.strftime("%Y-%m-%d %H:%M"),
            "valorTotal": float(r.valorTotal),
            "abono": float(r.abono),
            "saldo": float(r.saldo),
            "celular": r.celular,
            "telefono": r.telefono,
            "observaciones": r.observaciones,
            "vendedor": r.vendedor,
            "finalizada": r.finalizada
        }
        for r in registros
    ]