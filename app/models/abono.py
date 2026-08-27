from datetime import datetime

from app.database.db import db


class Abono(db.Model):
    __tablename__ = "abonos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orden_id = db.Column(db.Integer, db.ForeignKey("arreglos.id"), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now, nullable=False)