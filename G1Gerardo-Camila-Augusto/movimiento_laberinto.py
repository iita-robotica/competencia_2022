import time
from controller import Robot, DistanceSensor
from controller import Motor

robot = Robot()
timeStep = 32
noventaGrados = 14.8
tilesize = 0.06

destino_x = 0.0
destino_y = -4.0

gps = robot.getDevice("gps")
gps.enable(timeStep)

ruedaIzquierda = robot.getDevice("wheel1 motor")
ruedaDerecha = robot.getDevice("wheel2 motor")
ruedaIzquierda.setPosition(float('inf'))
ruedaDerecha.setPosition(float('inf'))

encoderIzquierdo = ruedaIzquierda.getPositionSensor()    
encoderDerecho = ruedaDerecha.getPositionSensor()
encoderIzquierdo.enable(timeStep)
encoderDerecho.enable(timeStep)

distance_sensor1 = robot.getDevice("distance sensor1")
distance_sensor1.enable(timeStep)

distance_sensor2 = robot.getDevice("distance sensor2")
distance_sensor2.enable(timeStep)

def avanzar(vel):
    ruedaIzquierda.setVelocity(vel)
    ruedaDerecha.setVelocity(vel)

def girar(vel):
        ruedaIzquierda.setVelocity(-vel)
        ruedaDerecha.setVelocity(vel)

robot.step(timeStep)
startX = gps.getValues()[0]/tilesize
startY = gps.getValues()[2]/tilesize

while robot.step(timeStep) != -1: 

    estado = "Primero"
    distance1 = distance_sensor1.getValue()

    distance2 = distance_sensor2.getValue()
    #print("Distance hacia la derecha 2: " + str(distance2))

    if distance1 > (tilesize/2) and estado == "Primero":
        print("Distancia sensor delantero: " + str(distance1))
        avanzar(1)
    
    elif distance1 < (tilesize/2):
        estado = "Segundo"
        while robot.step(timeStep) != -1:                                  
            avanzar(0)
            girar(0.5)
            print("Diferencia del encoder:", encoderDerecho.getValue() - noventaGrados)

            if(abs(encoderDerecho.getValue() - noventaGrados) < 0.01) and estado == "Segundo":
                avanzar(0)
                girar(0)
                estado = "Primero"
                break
