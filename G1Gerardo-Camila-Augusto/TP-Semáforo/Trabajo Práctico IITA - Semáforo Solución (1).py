# Grupo 1 - Instituto de Innovación y Tecnología Aplicada
#Semáforo
import time

estado = "Rojo"
contador = 0
contadorCiclo = 0
#Es el tiempo entre cada cambio de estado
tiempoEspara = 0.05

while contadorCiclo < 4:
    contador += 1
    if contador == 1 and estado == "Rojo":
        ''' Si el contador es igual a 1 y su estado es rojo, se logea el estado del semáforo y se cambia posteriormente a -Amarillo-'''
        print ("Estado actual del semáforo:", estado)
        estado = "Amarillo"
    
    elif contador == 2 and estado == "Amarillo":
        ''' Si el contador es igual a 2 y su estado es amarillo, se logea el estado del semáforo y se cambia posteriormente a -Verde-'''
        print ("Estado actual del semáforo:", estado)
        estado = "Verde"
    
    elif contador == 3 and estado == "Verde":
        ''' Si el contador es igual a 1 y su estado es verde, se logea el estado del semáforo y se establece nuevamente como -Rojo-. Se agrega una unidad
        al contador de ciclos cumplimentados'''
        print ("Estado actual del semáforo:", estado)
        contadorCiclo += 1
        print("- - - Ciclo número", contadorCiclo, "concluido. - - -")
        contador = 0
        estado = "Rojo"

    time.sleep(tiempoEspara)

print ("Programa terminado.")
