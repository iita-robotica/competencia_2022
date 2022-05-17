from controller import Robot, DistanceSensor

from controller import Robot, GPS
from controller import Motor
from controller import PositionSensor

robot = Robot()

timestep = 32
tilesize = 0.06

noventaGrados = 7.6

gps = robot.getDevice("gps")
gps.enable(timestep)

ruedaIzquierda = robot.getDevice("wheel1 motor")
ruedaDerecha = robot.getDevice("wheel2 motor")
ruedaIzquierda.setPosition(float('inf')) 
ruedaDerecha.setPosition(float('inf'))

encoderIzquierdo = ruedaIzquierda.getPositionSensor()
encoderDerecho = ruedaDerecha.getPositionSensor()
encoderIzquierdo.enable(timestep)
encoderDerecho.enable(timestep)

distance_sensor1 = robot.getDevice("distance sensor1")
distance_sensor1.enable(timestep)

distance_sensor2 = robot.getDevice("distance sensor2")
distance_sensor2.enable(timestep)

def avanzar (vel):
    ruedaIzquierda.setVelocity(vel)
    ruedaDerecha.setVelocity(vel)

def girar (vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)

estado = "estado_1"

while robot.step(timestep) != -1:

    distance1 = distance_sensor1.getValue()
    print("Distance hacia adelante 1: " + str(distance1))

    distance2 = distance_sensor2.getValue()
    print("Distance hacia la derecha 2: " + str(distance2))

    if distance1>0.06 and estado=="estado_1":
        avanzar (1.0)

    else:
        girar (0.5)
        estado="estado_2"
            
        if (abs(encoderDerecho.getValue() - noventaGrados) < 0.01):
            avanzar (0)
            girar(0)
            estado="estado_1"
