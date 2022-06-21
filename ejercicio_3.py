from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor

robot = Robot()

timeStep = 32

tilesize = 0.06

gps = robot.getDevice("gps")
gps.enable(timeStep)

robot.step(timeStep)

startX = gps.getValues()[0]/tilesize
startY = gps.getValues()[2]/tilesize
destino_x = 5.0
destino_y = -2.0

noventaGrados = 2.3

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

def avanzar(vel):
    ruedaIzquierda.setVelocity(vel)
    ruedaDerecha.setVelocity(vel)

def girar(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)

contador = 0

encoder_inicial = noventaGrados

estado="estado_0"

while robot.step(timeStep) != -1:

    x = round(gps.getValues()[0]/tilesize - startX, 1 )
    y = round(gps.getValues()[2]/tilesize - startY, 1 )

    print (x, " ", y)
    encoder_actual = encoderDerecho.getValue()
    
    if estado == "estado_0":
        ruedaDerecha.setPosition(float(noventaGrados))
        girar(0.5)
        print("Diferencia del encoder:", encoderDerecho.getValue() - encoder_inicial)
        if(abs(encoderDerecho.getValue() - noventaGrados) < 0.01):
            ruedaDerecha.setPosition(float('inf'))
            contador += 1
            estado = "estado_1"

    elif estado == "estado_1":
        distance = distance_sensor1.getValue()
        
        if distance > tilesize/2:
            avanzar(1)

            if (abs(x - destino_x) < 0.01) and (abs(y - destino_y) < 0.01):
                estado = "estado_0"
        
        else:
            avanzar(0)
            
            if contador == 1 or contador == 5:
                #encoder_inicial = 
                estado = "estado_0"
           
            elif contador > 1 and contador < 5:
                estado = "estado_2"
    
    elif estado == "estado_2":
        ruedaDerecha.setPosition(float(noventaGrados))
        girar(-0.5)

        if(abs(encoderDerecho.getValue() - noventaGrados) < 0.01):
            ruedaDerecha.setPosition(float('inf'))
            contador += 1
            estado = "estado_1"

    else:
        print("Error inesperado")
        break
    