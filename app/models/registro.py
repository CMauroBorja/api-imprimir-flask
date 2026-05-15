from datetime import datetime
from app.database.db import db


class Registro(db.Model):
    __tablename__ = "arreglos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreCliente = db.Column(db.String(100), nullable=False)
    fechaEntrega = db.Column(db.DateTime, nullable=False)
    fechaCreacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valorTotal = db.Column(db.Numeric(10, 2), nullable=False)
    abono = db.Column(db.Numeric(10, 2), nullable=False)
    saldo = db.Column(db.Numeric(10, 2), nullable=False)
    celular = db.Column(db.String(10), nullable=False)
    telefono = db.Column(db.String(16), nullable=True)
    observaciones = db.Column(db.UnicodeText(500), nullable=False)
    vendedor = db.Column(db.String(50), nullable=False)
    finalizada = db.Column(db.Boolean, default=False, nullable=False)
    medioPago = db.Column(db.String(20), nullable=False, default="efectivo")