import time

contador = 0

def cambio_estado (estado):
    while contador<12:
        print (estado)
        if estado=="rojo":
            estado="amarillo"
        elif estado=="amarillo":
            estado="verde"
        elif estado=="verde":
            estado="rojo"

cambio_estado("verde")