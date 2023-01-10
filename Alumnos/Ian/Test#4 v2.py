from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor
import math

robot = Robot()

timeStep = 32

tilesize = 0.06
tilesize_detection = tilesize/2

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

encoder = 2.215

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


encoder_goal = encoder 

state = "advance"

counter = 0

angulo = 0
angulo_posible = [0, 45, 90]
angulo_proximo = 0

diff_max = 0
diff_min = 0
prox_a = 0
prox_b = 0

def advance(vx, vy):
    ruedaIzquierda.setVelocity(vx)
    ruedaDerecha.setVelocity(vy)

def turn(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)
    
def get_angle():
    global x
    global y
    global x1
    global y1
    global angulo
    if x1 != x and y1 != y:
        angulo = math.atan2(abs(y1-y),abs(x1-x)) * 180/math.pi
    else:
        angulo = 0
    return angulo

def angle_normalizer(ang):
    ang = ang % 90
    if ang < 0:
        ang += 90
    return ang

def danger(image):
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    if (210 <= r <= 240) and (180 <= g <= 210) and (100 <= b <= 130):
        return True
    elif (r <= 47) and (g <= 47) and (b <= 47):
        return True


while robot.step(timeStep) != -1:
    encoder_actual = encoderDerecho.getValue()

    dis_frontal = distancia_frontal.getValue()
    dis_lateral = distancia_lateral.getValue()

    image = colorSensor.getImage()

    x = round(gps.getValues()[0]/tilesize - startX, 1 )
    y = round(gps.getValues()[2]/tilesize - startY, 1 )

    if 0 <= angulo < 30:
        angulo_proximo = 0
    elif 30 <= angulo <= 60:
        angulo_proximo = 45
    elif 60 < angulo <= 90:
        angulo_proximo = 90
        
    diff_max = angulo + 10
    diff_min = angulo - 10
    prox_a = diff_max - angulo_proximo
    prox_b = diff_min - angulo_proximo
    
    counter += 1

    if counter % 110 == 0 :
        get_angle()
        counter %= 5

    if state == "advance":
        print(angulo)
        if angulo not in angulo_posible:
            #print("angle")
            if (diff_max <= angulo_proximo) or (angulo_proximo <= diff_min):
                #print("fix")
                #analizar hacia que lado gira
                advance(1,1.05)
                if (abs(prox_a) <= 5) or (abs(prox_b) <= 5):
                    angulo = 0
        else:
            advance(1,1)
            
        if dis_frontal < tilesize_detection or danger(image):
            state = "turn"
            if dis_lateral < tilesize_detection:
                encoder_goal = encoder_actual - encoder
                turn(-0.5)
            else:
                encoder_goal = encoder_actual + encoder
                turn(0.5)

    elif state == "turn":
        angulo = 0
        if(abs(encoder_actual - encoder_goal) < turn_range):
            state = "advance"
            encoder_actual = 45
    