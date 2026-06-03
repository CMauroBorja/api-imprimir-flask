import re

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
        return False, "Los valores numéricos son inválidos"
    
def validar_celular(celular):
    return re.fullmatch(r"\d{10}", celular)

def validar_nombre_cliente(nombre):
    return len(nombre.strip()) >= 3

def validar_observaciones(observaciones):
    if len(observaciones) < 5:
        return False, (
            "Las observaciones deben tener al menos 5 caracteres"
        )

    if len(observaciones) > 500:
        return False, "Las observaciones no pueden exceder 500 caracteres"

    return True, ""