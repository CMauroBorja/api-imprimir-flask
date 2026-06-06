def validar_codigo(codigo):
    
    if not codigo:
        return False

    return bool(codigo.strip())


def validar_contrasena(contrasena):

    if not contrasena:
        return False

    return bool(contrasena.strip())


def validar_login(data):

    required_fields = [
        "codigo",
        "contrasena"
    ]

    if not data or any(
        field not in data
        for field in required_fields
    ):
        return (
            False,
            "Faltan datos requeridos"
        )

    if not validar_codigo(
        data["codigo"]
    ):
        return (
            False,
            "El código es obligatorio"
        )

    if not validar_contrasena(
        data["contrasena"]
    ):
        return (
            False,
            "La contraseña es obligatoria"
        )

    return (
        True,
        ""
    )