from controller import Robot
from controller import GPS
from controller import Motor
from controller import PositionSensor
from controller import DistanceSensor
import math

robot = Robot()

timeStep = 32
robot.step(timeStep)

tilesize = 0.06
tilesize_detection = tilesize/2

gps = robot.getDevice("gps")
gps.enable(timeStep)

startX = gps.getValues()[0]/tilesize
startY = gps.getValues()[2]/tilesize

turn_range = 0.01
turn_counter = 0

encoder = 2.215
encoder_goal = encoder 

x = 0
x1 = 0
y = 0
y1 = 0

angulo = 0
angulo_posible = [0, 45, 90]
angulo_proximo = 0

diff_max = 0
diff_min = 0

column = 0
column_max = 0
column_min = 0
column_total = 0

row = 0
row_max = 0
row_min = 0
row_total = 0
rows = []

point = 0
cardinal = "north"

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

state = "advance"

counter = 0


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
        
    diff_max = angulo + 12
    diff_min = angulo - 12
    
    counter += 1
    
    if column_max < column:
        column_max = column
    elif column < column_min:
        column_min = column
    column_total = abs(column_min) + column_max
        
    if row_max < row:
        row_max = row
    elif row < row_min:
        row_min = row
    row_total = abs(row_min) + row_max
    
    if (4 <= point) or (point <= -5):
        point = 0
    
    if point == 0 or point == -4:
        cardinal = "north"
    elif point == 1 or point == -3:
        cardinal = "east"
    elif point == 2 or point == -2:
        cardinal = "south"
    elif point == 3 or point == -1:
        cardinal = "west"

    if counter % 110 == 0 :
        get_angle()
        counter %= 5

    if state == "advance":
        print(angulo)
        if angulo not in angulo_posible:
            state = "advance_fix"
            if (diff_max <= angulo_proximo) or (angulo_proximo <= diff_min):
                if turn_counter == 20:
                    turn_counter = 0
                    advance(1,0.97)
                else:
                    advance(1,1)
        else:
            advance(1,1)
            
        if dis_frontal < tilesize_detection or danger(image):
            state = "turn"
            if dis_lateral < tilesize_detection:
                encoder_goal = encoder_actual - encoder
                turn_counter += 1
                point -= 1
                turn(-0.5)
            else:
                encoder_goal = encoder_actual + encoder
                turn_counter += 1
                point += 1
                turn(0.5)
                
        #print("punto=", point)
        #print(cardinal)
        for i in range(row_total):
            rows.append(row)
        
    elif state == "turn":
        angulo = 0
        if(abs(encoder_actual - encoder_goal) < turn_range):
            state = "advance"
            encoder_actual = 45
    
    elif state == "advance_fix":
        if (angulo_proximo < diff_max) or (diff_min < angulo_proximo):
            state = "advance"
            angulo = 0
            