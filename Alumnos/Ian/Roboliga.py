from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor
import math

robot = Robot()

timeStep = 32

tilesize = 0.06
half_tilesize = tilesize/2


gps = robot.getDevice("gps")
gps.enable(timeStep)

robot.step(timeStep)

startX = gps.getValues()[0]/tilesize
startY = gps.getValues()[2]/tilesize

x = 0
x1 = 0
y = 0
y1 = 0


turn_range = 0.01

encoder = 2.3


ruedaIzquierda = robot.getDevice("wheel1 motor")
ruedaIzquierda.setPosition(float('inf'))
ruedaDerecha = robot.getDevice("wheel2 motor")
ruedaDerecha.setPosition(float('inf'))


encoderIzquierdo = ruedaIzquierda.getPositionSensor()
encoderIzquierdo.enable(timeStep)
encoderDerecho = ruedaDerecha.getPositionSensor()
encoderDerecho.enable(timeStep)


distancia_frontal = robot.getDevice("distance sensor1")
distancia_frontal.enable(timeStep)
distancia_lateral = robot.getDevice("distance sensor2")
distancia_lateral.enable(timeStep)


colorSensor = robot.getDevice("colour_sensor")
colorSensor.enable(timeStep)



def advance(vx, vy):
    ruedaIzquierda.setVelocity(vx)
    ruedaDerecha.setVelocity(vy)

def turn(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)

def goal(x1,x,y1,y):
    if (y1-y) != 0:
        alpha = math.atan2((x1-x),(y1-y))
    else:
        alpha = 0
    return alpha

def danger(image):
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    #Buscar los margenes para en rgb para el hueco
    return ( 210 <= r <= 240) and (180 <= g <= 210) and (100 <= b <= 130)


encoder_goal = encoder 

state = "advance"


def angle_normalizer(ang):
    ang = ang % 360
    if ang < 0:
        ang += 360
    return ang

def get_angle():
    global x
    global y
    global x1
    global y1
    global angulo
    if x1 != x or y1 != y:
        #print(f'Valores de la posicion inicial y final: (x, x1 , y, y1) : {x}, {x1}, {y}, {y1}')
        angulo = math.atan2(y-y1,x-x1) * 180/math.pi
        #print(f'Current Angle:  {math.atan2(y-y1,x-x1)} rad to deg: {angulo}')
    return angulo


counter = 0
angulo = 0



while robot.step(timeStep) != -1:
    encoder_actual = encoderDerecho.getValue()

    dis_frontal = distancia_frontal.getValue()
    dis_lateral = distancia_lateral.getValue()

    image = colorSensor.getImage()

    x = round(gps.getValues()[0]/tilesize - startX, 1 )
    y = round(gps.getValues()[2]/tilesize - startY, 1 )

    counter += 1
    #print(f'Counter value: {counter}')


    if counter % 110 == 0 :
        #print(f'Valores de la posicion inicial y final: (x, x1 , y, y1) : {x}, {x1}, {y}, {y1}')
        get_angle()
        x1 = x
        y1 = y
        counter %= 5


    if state == "advance":

        if angulo not in [0, 90, 180, 270]:
            valor_proximo = min([0, 90, 180, 270], key=angulo)
            #print(f'Valor mas proximo a mi angulo deseado: {valor_proximo}')
        advance(0.5,0.5)

        if dis_frontal < half_tilesize or danger(image):
            state = "turn"
            if dis_lateral < half_tilesize:
                encoder_goal = encoder_actual - encoder
                turn(-0.5)
            else:
                encoder_goal = encoder_actual + encoder
                turn(0.5)

    elif state == "turn":
        if(abs(encoder_actual - encoder_goal) < turn_range):
            state = "advance"



    # Resolver como advance en forma recta sobre alguno de los ejes (x o y)
    # Es decir debemos corregir luego de un turn que el desplazamiento vaya sobre un unico eje.
