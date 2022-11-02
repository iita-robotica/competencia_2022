from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor

robot = Robot()

timeStep = 32

# Longitud de la baldoza
tilesize = 0.06

# Cargamos el controlador del gps
gps = robot.getDevice("gps")
# Habilitamos el gpss
gps.enable(timeStep)

# Actualizamos los valores del gps
robot.step(timeStep)

# Guardamos los valores iniciales del GPS
#  (Posicion inicial del robot)
startX = gps.getValues()[0]/tilesize
startY = gps.getValues()[2]/tilesize

# Coordenadas del punto 3 de la imagen del ejercicio 3
destino_x = 9.6
destino_y = -0.2

# Delta ( x1 - x0) -> variacion que se requiere para
# girar 90 grados utilizando el encoder
noventaGrados = 2.3

# Inicializamos los motores
ruedaIzquierda = robot.getDevice("wheel1 motor")
ruedaDerecha = robot.getDevice("wheel2 motor")
# El valor de 'inf' nos permite que las ruedas giren libremente
# Si se setea un valor fijo una vez alcanzodo dicho valor las ruedas estaran bloqueadas
ruedaIzquierda.setPosition(float('inf'))
ruedaDerecha.setPosition(float('inf'))

# Inicializo el encoder -> es obtenido de los motores
encoderIzquierdo = ruedaIzquierda.getPositionSensor()
encoderDerecho = ruedaDerecha.getPositionSensor()
encoderIzquierdo.enable(timeStep)
encoderDerecho.enable(timeStep)

# Inicializo sensor de distancia
distance_sensor1 = robot.getDevice("distance sensor1")
distance_sensor1.enable(timeStep)

# Metodos/funciones utiles para mi programa
def avanzar(vel):
    ruedaIzquierda.setVelocity(vel)
    ruedaDerecha.setVelocity(vel)

def girar(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)


contador_giro = 0 # determina el sentido (ver gráfico)
# Se usa para realizar un cambio de estado cuando estamos
#   llegando al punto 3 de la imagen (previo al giro)
bloqueo_ciclo = 1 # evita un retorno de la función (línea 91)

encoder_goal = noventaGrados # es el próximo valor que deseamos alcanzar en la siguiente rotación

estado="giro_derecha" # Estado inicial

while robot.step(timeStep) != -1:

    # Actualizacion del entorno:
        # Encoder
        # Sensores de distancia

    # Estados:
        # 1. Avanzar
            # Cambio de etado:
                # Proximo a chocar una pared -> Usa sensor distancia
                # Validar proxima baldoza no sea un hueco -> Sensor Color
            # Proximo estado:
                # Girar -> Izq o Der
            # Acciones:
                #  Avanzar
        # 2. Girar a la derecha
                # ........ Agregar pseudocodigo .....



