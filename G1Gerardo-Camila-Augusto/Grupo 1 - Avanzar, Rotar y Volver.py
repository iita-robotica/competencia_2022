from controller import Robot, GPS
from controller import Motor
from controller import PositionSensor

robot = Robot()
timeStep = 32
noventaGrados = 16.5
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

    x = round( gps.getValues()[0]/tilesize - startX, 1 )
    y = round( gps.getValues()[2]/tilesize - startY, 1 )

    if ( x == destino_x) and ( y == destino_y ): #Si el Robot no esta en determinada posicion avanza. Una vez llega a destino

        while robot.step(timeStep) != -1:
                                                #Deja de avanzar y empieza a girar 90 grados
            avanzar(0)
            girar(0.5)
            print("Diferencia del encoder:", encoderDerecho.getValue() - noventaGrados) #Esta es la linea para girar 90 grados 

            if(abs(encoderDerecho.getValue() - noventaGrados) < 0.01): #Una vez giro 90 grados avanza indefinidamente
                avanzar(1)
                break 
            break

    else:
        avanzar(1)










