from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor

robot = Robot()

timeStep = 32

# Longitud de la baldoza
tilesize = 0.06
media_baldoza = tilesize/2

# Defino margenes
margen_de_giro = 0.01

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
distancia_frontal = robot.getDevice("distance sensor1")
distancia_frontal.enable(timeStep)
distancia_lateral = robot.getDevice("distance sensor2")
distancia_lateral.enable(timeStep)


# Step 2: Inicializo el sensor de color
colorSensor = robot.getDevice("colour_sensor")
colorSensor.enable(timeStep)

# Metodos/funciones utiles para mi programa
def avanzar(vel):
    ruedaIzquierda.setVelocity(vel)
    ruedaDerecha.setVelocity(vel)

def girar(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)

def proxima_baldoza_es_un_hueco(imagen):
    # Clasifico el codigo de color en RGB
    r = colorSensor.imageGetRed(imagen, 1, 0, 0)
    g = colorSensor.imageGetGreen(imagen, 1, 0, 0)
    b = colorSensor.imageGetBlue(imagen, 1, 0, 0)
    # TODO: Buscar los margenes para en rgb para el hueco
    return ( 210 <= r  <= 240) and  (180 <= g <= 210) and (100 <= b <= 130)

contador_giro = 0 # determina el sentido (ver gráfico)
# Se usa para realizar un cambio de estado cuando estamos
#   llegando al punto 3 de la imagen (previo al giro)
bloqueo_ciclo = 1 # evita un retorno de la función (línea 91)

encoder_goal = noventaGrados # es el próximo valor que deseamos alcanzar en la siguiente rotación

estado="avanzar" # Estado inicial

while robot.step(timeStep) != -1:

    # Actualizo el valor del encoder
    encoder_actual = encoderDerecho.getValue()
    # Actualizo el sensores de distancia
    dis_frontal = distancia_frontal.getValue()
    dis_lateral = distancia_lateral.getValue()
    # Actualizo los valores del sensor de color
    imagen = colorSensor.getImage()



    if estado == "avanzar":
        # Acciones:
        avanzar(1)

        # Cambio de etado:
        # Proximo a chocar una pared o hay un hueco en la proxima baldoza
        if dis_frontal < media_baldoza or proxima_baldoza_es_un_hueco(imagen):
            estado = "giro"

    # 2. Girar a la derecha
    elif estado == "giro_izquierda":
        # Accion: girar a la izquierda
        girar(-0.5)

        # Cambio de estado?
        # Cuando completa el giro de los 90 grados a la izquierda
        if(abs(encoder_actual - encoder_goal) < margen_de_giro):
            estado = "avanzar"

    # 2. Girar
    elif estado == "giro":
        # Cuando completa el giro de los 90 grados a la izquierda

        # Giro a la izquierda si a la derecha hay pared
        if dis_lateral < media_baldoza:
            # Actualizo valor del encoder para un giro de 90 grados a la izquierda
            encoder_goal = encoder_actual - noventaGrados
            girar(-0.5)
        else:
            # Actualizo valor del encoder para un giro de 90 grados a la derecha
            encoder_goal = encoder_actual + noventaGrados
            girar(0.5)

        if(abs(encoder_actual - encoder_goal) < margen_de_giro):
            estado = "avanzar"


# TODO: Encontrar porque el robot queda bloqueado cuando esta girando cerca  del pantano!



