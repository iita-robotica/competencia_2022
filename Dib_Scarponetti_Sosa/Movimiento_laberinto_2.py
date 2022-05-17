from controller import Robot, GPS
from controller import Motor
from controller import PositionSensor

timestep = 32
tilesize = 0.06

timeStep = 32 
noventaGrados = 7.6
robot = Robot()

gps = robot.getDevice("gps")
gps.enable(timestep)

destino_x = 0.0
destino_y = -4.0

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

robot.step(timestep)
startX = gps.getValues()[0]/tilesize
startY = gps.getValues()[2]/tilesize

while robot.step(timestep) != -1:

    x = round( gps.getValues()[0]/tilesize - startX, 1 )
    y = round( gps.getValues()[2]/tilesize - startY, 1 )

    if ( x == destino_x) and ( y == destino_y ):
        while robot.step(timestep) != -1:
            avanzar(0)
            girar(0.5)
            print("Diferencia del encoder:", encoderDerecho.getValue() - noventaGrados  )
            
            if(abs(encoderDerecho.getValue() - noventaGrados) < 0.01):
                print ("Giro")
                avanzar(1.0)
                break
        
            break

    else:
        avanzar(1.0)

    print("Imprimo la posicion actual x:", x,"y:", y)
    