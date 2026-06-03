def validar_datos_numericos(data):
    try:
        valor_total = float(data["valorTotal"])
        abono = float(data["abono"])
        saldo = float(data["saldo"])

        if valor_total <= 0:
            return False, "El valor total debe ser mayor que 0"

        if abono < 0:
            return False, "El abono no puede ser negativo"

        if saldo < 0:
            return False, "El saldo no puede ser negativo"

        if abs(saldo - (valor_total - abono)) > 0.01:
            return False, (
                "El saldo debe ser igual "
                "al valor total menos el abono"
            )

        return True, ""

    except ValueError:
        return False, (
            "Los valores numéricos son inválidos"
        )