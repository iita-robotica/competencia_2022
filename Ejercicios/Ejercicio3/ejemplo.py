"""
Pseudo codigo:
# Inicializo:
* Motores
* Encoders
* Sensor distancia frontal

Metodos a utilizar:
* Avanzar
* Rotar
* Deteccion objeto frontal

Estados:
    Rotacion
    Avanzo


estado = rotacion

Mientras estado != final:
    si estado == inicial:
        si giro 90 esta completado
            estado = avanzo_1

    si etado == avanzo_1:
        si distancia > 1/2 baldoza:
            avanzo
        sino:
            estado = giro_2



"""
from cmath import inf
from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor

robot = Robot() # Create robot object
timeStep = 32   # timeStep = numero de milisegundos entre actualizaciones mundiales (del mundo)
noventaGrados = 2.3
longitud_baldoza = 0.06


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

# Inicializo sensor distancia frontal
distance_sensor1 = robot.getDevice("distance sensor1")
distance_sensor1.enable(timeStep)

#Create your code here
def avanzar(vel):
    ruedaIzquierda.setVelocity(vel)
    ruedaDerecha.setVelocity(vel)

def girar(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)


estado="inicial"

while robot.step(timeStep) != -1 and estado != "final":


    if estado == "inicial":
        # Defino la posision que deberia llegar el encoder
        ruedaDerecha.setPosition(float(noventaGrados))
        # Configuro la velocidad de las ruedas
        girar(0.5)
        print("Diferencia del encoder:", encoderDerecho.getValue() - noventaGrados  )
        # Si se roto los 90 grados con un margen de 0.01 me detengo
        if(abs(encoderDerecho.getValue() - noventaGrados) < 0.01):
            # Libero rotacion de las rueda
            ruedaDerecha.setPosition(float('inf'))
            # Paso al estado siguiente
            estado = "avanzo_1"

    elif estado == "avanzo_1":
        distancia_fronta = distance_sensor1.getValue()
        if distancia_fronta  > longitud_baldoza/2:
            avanzar(1)
        else:
            avanzar(0)
            estado = "final"
    else:
        print("Error inesperado")
        break




