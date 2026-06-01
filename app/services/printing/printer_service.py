import time
from app.services.printing.windows_printer import (
    enviar_a_impresora
)
from app.services.printing.ticket_builder import (
    construir_ticket_cliente, 
    construir_ticket_negocio
)


def imprimir_registro(registro, solo_negocio=False, cantidad_copias=1):
    """Imprime tickets ESC/POS -- impresora térmica DIG-E200I"""
    
    contenido_cliente = construir_ticket_cliente(registro)

    contenido_negocio = construir_ticket_negocio(registro)

    try:
        # Primero imprimir la copia del cliente (si aplica)
        if not solo_negocio:
            enviar_a_impresora(contenido_cliente,"Ticket Cliente")
            time.sleep(0.5)

        # Luego imprimir las copias del negocio según cantidad_copias
        for i in range(cantidad_copias):
            enviar_a_impresora(contenido_negocio,"Ticket Negocio")
            if i < cantidad_copias - 1:  # No esperar después de la última impresión
                time.sleep(0.5)
    except Exception as e:
        raise RuntimeError(f"Error al imprimir: {e}") from e
        
        
       
def imprimir_solo_cliente(registro):
    """Imprime únicamente la copia del cliente.""" 
    
    contenido_cliente = construir_ticket_cliente(registro)

    try:
        enviar_a_impresora(contenido_cliente,"Ticket Cliente")
    except Exception as e:
        raise RuntimeError(f"Error al imprimir ticket del cliente: {e}") from e
    
