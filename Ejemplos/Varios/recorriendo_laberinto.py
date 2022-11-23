from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor
import math

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
def avanzar(vx, vy):
    ruedaIzquierda.setVelocity(vx)
    ruedaDerecha.setVelocity(vy)

def girar(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)

# Ir  a la meta
def go_to_gaol(x1,x,y1,y):
    # delta x
    # delta y
    # alfa = arctg (delta x / delta y)
    if (y1-y) != 0:
        alpha = math.atan2((x1-x),(y1-y))
    else:
        alpha = 0

    # avanzar(vx*fx, vy*fy))
    return alpha
    # pass

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
    # Actualizo valores de GPS traducidos en baldozas
    x = round(gps.getValues()[0]/tilesize - startX, 1 )
    y = round(gps.getValues()[2]/tilesize - startY, 1 )


    print("Alfa: ", go_to_gaol(0,x,1,y))
    print(f'(x,y)= ({x},{y}')

    # si llegue a la meta
        # definir proxima meta
    # sino
        # sigo hacie la meta



    if estado == "avanzar":
        # Acciones:
        avanzar(0.5,0.5)

        # Cambio de etado:
        # Proximo a chocar una pared o hay un hueco en la proxima baldoza
        if dis_frontal < media_baldoza or proxima_baldoza_es_un_hueco(imagen):
            estado = "giro"
            # Giro a la izquierda si a la derecha hay pared
            if dis_lateral < media_baldoza:
                # Actualizo valor del encoder para un giro de 90 grados a la izquierda
                encoder_goal = encoder_actual - noventaGrados
                girar(-0.5)
            else:
                # Actualizo valor del encoder para un giro de 90 grados a la derecha
                encoder_goal = encoder_actual + noventaGrados
                girar(0.5)

    # 2. Girar
    elif estado == "giro":
        # Cuando completa el giro de los 90 grados a la izquierda
        if(abs(encoder_actual - encoder_goal) < margen_de_giro):
            estado = "avanzar"


# TODO(lchico/tarea_proxima_clase_22_11_22):
    # Resolver como avanzar en forma recta sobre alguno de los ejes (x o y)
    # Es decir debemos corregir luego de un giro que el desplazamiento vaya sobre un unico eje.



# Nota:
# 1. Definir la condicion de giro dentro del mismo esta en el que giramos
# 2. Crear un nuevo estado donde seleccionamos el sentido del giro y luego cambiamos al estado de giro


# TODO:(lchico/tarea_proxima_clase_15_11_22) Encontrar porque el robot queda bloqueado cuando esta girando cerca  del pantano!
# 1. Gerardo ->
#     a) linea 129  -> estados repetidos
# 2. Ian:
#   a) El estado giro izquierda esta de mas
#   b) Comparacion del encoder
#   c) Argumento del color
# 3. Ignacio:
#   a) Problema del giro no esta solo con el pantano
#   b) Gira de mas
#   c) Giro indefinido para un lado y para el otro
# 4. Maximo:
#   a)



