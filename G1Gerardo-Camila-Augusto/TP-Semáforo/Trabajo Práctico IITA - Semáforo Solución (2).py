# Grupo 1 - Instituto de Innovación y Tecnología Aplicada
#Semáforo
import time

estado = "Rojo"
contadorCiclo = 1

while contadorCiclo < 5:
    if estado == "Rojo":
        print("- - - Ciclo número", contadorCiclo, "concluido. - - -")
        ''' Si el contador es igual a 1 y su estado es rojo, se logea el estado del semáforo y se cambia posteriormente a -Amarillo-'''
        print ("Estado actual del semáforo:", estado)
        estado = "Amarillo"
    
    elif estado == "Amarillo":
        ''' Si el contador es igual a 2 y su estado es amarillo, se logea el estado del semáforo y se cambia posteriormente a -Verde-'''
        print ("Estado actual del semáforo:", estado)
        estado = "Verde"
    
    elif estado == "Verde":
        ''' Si el contador es igual a 1 y su estado es verde, se logea el estado del semáforo y se establece nuevamente como -Rojo-. Se agrega una unidad
        al contador de ciclos cumplimentados'''
        print ("Estado actual del semáforo:", estado)
        contadorCiclo += 1
        estado = "Rojo"

    time.sleep(50)
    
print ("Programa terminado.")
