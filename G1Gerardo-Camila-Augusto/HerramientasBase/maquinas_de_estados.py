#!/bin/python
import time

estado = "Inicial"

#contador = 0
contadorCiclos = 0

while contadorCiclos < 4 :
    #contador+=1
    # Valido si estoy en el estado inicial
    if estado == "Inicial":
        # Tareas que realizo en el estado inicial
        
            print("1")
            estado = "primero"

    # Valido si estoy en el estado primero
    elif estado == "primero":
        # Tareas que realizo en el estado "primero"
        
        
            print("2")
            estado = "segundo"

    # Valido si estoy en el estado "segundo"
    elif estado == "segundo":
        # Tareas que realizo en el estado "segundo"
        
        
            print("3")
            contadorCiclos += 1
            estado = "Inicial"
            #contador = 0
            print(estado)

    
    time.sleep(0.05)

print("Programa terminado")






