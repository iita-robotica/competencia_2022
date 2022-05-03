import time

estado = "verde"

contador = 0

while contador<12:
    if estado == "verde":
        print("Estado semáforo:", estado)
        estado = "amarillo"

    elif estado == "amarillo":
        print("Estado semáforo:", estado)
        estado = "rojo"

    elif estado == "rojo":
        print("Estado semáforo:", estado)
        estado = "verde"

    contador+=1
    time.sleep(3)

print("Programa terminado")