from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor
import math

robot = Robot()

timeStep = 32

tilesize = 0.06 # Probar 0.10 | 0.9
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

encoder = 2.215 #Original 2.3

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
distancia_lateralIzq = robot.getDevice("distance sensor3")
distancia_lateralIzq.enable(timeStep)

colorSensor = robot.getDevice("colour_sensor")
colorSensor.enable(timeStep)


encoder_goal = encoder 

state = "advance"

counter = 0

angulo = 0

savedPlaces = []

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
    if x1 != x or y1 != y:
        angulo = math.atan2(y1-y,x1-x) * 180/math.pi
    return angulo

def angle_normalizer(ang):
    ang = ang % 360
    if ang < 0:
        ang += 360
    return ang

def danger(image):
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)
    
    #Reconocimiento de obstáculos
    if ( 210 <= r  <= 240) and  (180 <= g <= 210) and (100 <= b <= 130):
        return True
    elif (r <= 47) and (g <= 47) and (b <= 47):
        return True

while robot.step(timeStep) != -1:
    encoder_actual = encoderDerecho.getValue()

    dis_frontal = distancia_frontal.getValue()
    dis_lateral = distancia_lateral.getValue()
    dis_latIzq = distancia_lateralIzq.getValue()

    print(f'Frontal = {dis_frontal:.3f}, Derecha = {dis_lateral:.3f}, Izquierda = {dis_latIzq:.3f}')

    image = colorSensor.getImage()

    x = round(gps.getValues()[0]/tilesize - startX, 1 )
    y = round(gps.getValues()[2]/tilesize - startY, 1 )

    counter += 1

    if counter % 110 == 0 :
        #print(f'Valores de la posicion inicial y final: (x, x1 , y, y1) : {x}, {x1}, {y}, {y1}')
        get_angle()
        #x1 = x
        #y1 = y
        counter %= 5

    if state == "advance":
        # print(angulo)
        if angulo not in [0, 45, 90, 135, 180, 215, 270, 315]:
            advance(1,1)
            #valor_proximo = min([0, 90, 180, 270], key=angulo)
            #print(f'Valor mas proximo a mi angulo deseado: {valor_proximo}')
        else:
            advance(1,1)
            
        if dis_frontal < half_tilesize or danger(image):
            state = "turn"
            if dis_lateral < half_tilesize:
                encoder_goal = encoder_actual - encoder
                turn(-0.5)
                savedPlaces.append((x,y))
            else:
                encoder_goal = encoder_actual + encoder
                turn(0.5)

    elif state == "turn":
        # print("Valores: ", encoderDerecho.getValue(), encoderIzquierdo.getValue())
        if(abs(encoder_actual - encoder_goal) < turn_range):
            state = "advance"
            encoder_actual = 45

    