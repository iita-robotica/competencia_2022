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
    # Actualizar la posicion del robot en base a la posicion inicial del robot
    # Utilizando (startX, Starty) traslado el origen del GPS a la posicion incial del robot
    # Es decir ahora (x, y) tienen el origen donde esta el robot inicialmente.
    x = round(gps.getValues()[0]/tilesize - startX, 1 )
    y = round(gps.getValues()[2]/tilesize - startY, 1 )

    #  Actualizo el valor del encoder
    encoder_actual = encoderDerecho.getValue()

    # Nucleo de nuestro programa
    # Estados:
        #   1. giro_derecha:
                # Cambio de estado en funcion del encoder
                # Proximo estado: avanzar
                # Accion -> Gira a la derecha y cuenta giro
        #   2. avanzar:
                # a.  Actualizamos sensor distancia
                # b. Cambio de estado:
                    #  Depende del sensor distancia
                        # giro_derecha: -> depende del contador giro (1 o 5)
                        # giro_izquierda: -> depende del contador giro (2 3 4)

                    #  Depende la distancia a la coordenada proxima al punto 3 (bloqueo_ciclo)
                # Accion -> Setea el nuevo encoder_goal y pasa a un estado de giro.
        #   3. giro_izquierda:
                # Cambio de estado en funcion del encoder
                # Proximo estado: avanzar
                # Accion -> Gira a la izquierda y cuenta giro

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
