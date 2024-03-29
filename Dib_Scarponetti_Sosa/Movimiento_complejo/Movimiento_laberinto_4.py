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
destino_x = 9.6
destino_y = -0.2

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

contador_giro = 0 # determina el sentido (ver gráfico)
bloqueo_ciclo = 1 # evita un retorno de la función (línea 75)

encoder_goal = noventaGrados # es el próximo valor que deseamos alcanzar en la siguiente rotación

estado="giro_derecha"

while robot.step(timeStep) != -1:

    x = round(gps.getValues()[0]/tilesize - startX, 1 )
    y = round(gps.getValues()[2]/tilesize - startY, 1 )

    encoder_actual = encoderDerecho.getValue()
    
    if estado == "giro_derecha":
        girar(0.5)
        if(abs(encoder_actual - encoder_goal) < 0.01):
            ruedaDerecha.setPosition(float('inf'))
            contador_giro += 1
            estado = "avanzar"

    elif estado == "avanzar":
        distance = distance_sensor1.getValue()
        
        if distance > tilesize/2:
            avanzar(1)
            if (abs(x - destino_x) < 0.2) and (abs(y - destino_y) < 0.2) and bloqueo_ciclo==1: # esto sucede en la parte final (previo a 3)
                bloqueo_ciclo = 0
                encoder_goal = encoder_actual + noventaGrados
                estado = "giro_derecha"
        
        else:
            avanzar(0)
            if contador_giro == 1 or contador_giro == 5:
                encoder_goal = encoder_actual + noventaGrados # actualización del encoder al nuevo valor deseado (el encoder va subiendo)
                estado = "giro_derecha"
            elif contador_giro > 1 and contador_giro < 5:
                encoder_goal = encoder_actual - noventaGrados # al ser un giro a la izquierda, el signo es contrario
                estado = "giro_izquierda"
    
    elif estado == "giro_izquierda":
        girar(-0.5)
        if(abs(encoder_actual - encoder_goal) < 0.01):
            ruedaDerecha.setPosition(float('inf'))
            contador_giro += 1
            estado = "avanzar"

    else:
        print("Error inesperado")
        break
    