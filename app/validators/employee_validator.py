import re


def validar_nombre(nombre):

    if not nombre:
        return False

    return len(nombre.strip()) >= 3


def validar_telefono(telefono):

    if not telefono:
        return False

    return bool(
        re.fullmatch(
            r"\d{10}",
            telefono.strip()
        )
    )


def validar_codigo(codigo):

    if not codigo:
        return False

    return len(codigo.strip()) >= 3


def validar_contrasena(contrasena):

    if not contrasena:
        return False

    return len(contrasena.strip()) >= 4