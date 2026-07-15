def serialize_order(registro):
    return {
        "id": registro.id,
        "nombreCliente": registro.nombreCliente,
        "fechaEntrega": registro.fechaEntrega.strftime(
            "%Y-%m-%d %H:%M"
        ),
        "fechaCreacion": registro.fechaCreacion.strftime(
            "%Y-%m-%d %H:%M"
        ),
        "valorTotal": float(
            registro.valorTotal
        ),
        "abono": float(
            registro.abono
        ),
        "saldo": float(
            registro.saldo
        ),
        "celular": registro.celular,
        "telefono": registro.telefono,
        "observaciones": registro.observaciones,
        "vendedor": registro.vendedor,
        "finalizada": registro.finalizada
    }


def serialize_order_list(registros):
    return [
        serialize_order(registro)
        for registro in registros
    ]