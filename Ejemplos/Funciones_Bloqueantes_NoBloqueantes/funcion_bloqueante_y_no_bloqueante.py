#!/bin/python
import time


contador = 0
objetivo_contador = 3

def tarea():
    global contador
    print(contador)
    contador+=1
    time.sleep(0.1)

def bloqueante():
    global contador
    while (contador < objetivo_contador):
        tarea()   # increamento el contador

def no_bloqueante():
    global contador
    if (contador < objetivo_contador):
        tarea()  # incremento el contador
        return False
    else:
        return True


print(" Funcion no bloqueante")
print("hola")
while True:
    ret = no_bloqueante()
    print("Trabajando...")
    if ( ret == True ):
        print("mundo")
        break

print("Funcion bloqueante")

#Reinicio contador para evaluar el segundo caso
contador = 0

# Funcion bloqueante
print("hola")
while True:
    bloqueante()
    print("Trabajando...")
    if(contador >= objetivo_contador):
      print("mundo")
      break


