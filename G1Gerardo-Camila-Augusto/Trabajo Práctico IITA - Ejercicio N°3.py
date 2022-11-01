from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor

robot = Robot() # Create robot object
timeStep = 32   # timeStep = numero de milisegundos entre actualizaciones mundiales (del mundo)
noventaGrados = 2.5
longitud_baldoza = 0.06

gps = robot.getDevice("gps")
gps.enable(timeStep)

estado = "Inicial"

# Inicializo Motores
ruedaIzquierda = robot.getDevice("wheel1 motor")
ruedaDerecha = robot.getDevice("wheel2 motor")
ruedaIzquierda.setPosition(float('inf'))
ruedaDerecha.setPosition(float('inf'))

# Inicializo los encoders
encoderIzquierdo = ruedaIzquierda.getPositionSensor()
encoderDerecho = ruedaDerecha.getPositionSensor()
encoderIzquierdo.enable(timeStep)
encoderDerecho.enable(timeStep)

encoderValorInicial = encoderDerecho.getValue() #Guardo el valor inicial en una variable

# Inicializo sensor distancia frontal
distance_sensor1 = robot.getDevice("distance sensor1")
distance_sensor1.enable(timeStep)

robot.step(timeStep)
startX = gps.getValues()[0]/longitud_baldoza
startY = gps.getValues()[2]/longitud_baldoza

def avanceRobot(velocidad):
    ruedaIzquierda.setVelocity(velocidad)
    ruedaDerecha.setVelocity(velocidad)

def rotacionRobotDerecha(velocidad):
    ruedaIzquierda.setVelocity(-velocidad)
    ruedaDerecha.setVelocity(velocidad)

def rotacionRobotIzquierda(velocidad):
    ruedaIzquierda.setVelocity(velocidad)
    ruedaDerecha.setVelocity(-velocidad)

wayPoint = "First"
contador = 0

while robot.step(timeStep) != -1:
    distancia = distance_sensor1.getValue()
    # encoderActual = encoderDerecho.getValue()
    if estado == "Inicial":
        rotacionRobotDerecha(0.3)
        print("Diferencia del encoder:", encoderDerecho.getValue() - noventaGrados  )
        if(abs(encoderDerecho.getValue() - noventaGrados) < 0.01):
            estado = "MidiendoDistancia"
    
    elif estado == "MidiendoDistancia":
        if distancia > (longitud_baldoza)/2:
            avanceRobot(1)

        elif distancia < (longitud_baldoza/2) and wayPoint == "First":
            encoderActual = encoderDerecho.getValue()
            estado = "RotarDerecha"

        elif distancia < (longitud_baldoza/2) and wayPoint == "Second":
            encoderActual = encoderDerecho.getValue()
            estado = "RotarIzquierda"
    
    elif estado == "RotarDerecha" and wayPoint == "First":
        # print(encoderActual - encoderValorInicial)
        # print("Diferencia del encoder:", encoderActual - encoderValorInicial)
        # print("Diferencia del encoder:", -(encoderDerecho.getValue()) + noventaGrados  ) ¿Solución?
        rotacionRobotDerecha(0.5)
        print("Diferencia del encoder:", encoderDerecho.getValue() - noventaGrados)
        if (abs((encoderDerecho.getValue() - encoderActual) - noventaGrados) <= 0.10):
            print("Rotación completada")
            avanceRobot(0)
            estado = "MidiendoDistancia"
            wayPoint = "Second"
    
    elif estado == "RotarIzquierda" and wayPoint == "Second":
        rotacionRobotIzquierda(1)
        print ("Diferencia del enconder:", encoderActual - noventaGrados)
        if (abs((encoderDerecho.getValue() - encoderActual) + noventaGrados) <= 0.3):
            print("Rotación completada")
            contador += 1
            print(contador)
            if contador >= 4:
                estado = "RotarDerecha"
                wayPoint = "First"
            else:
                estado = "MidiendoDistancia"
        
