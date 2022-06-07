from controller import Robot, GPS

timestep = 32
tilesize = 0.06

robot = Robot()

gps = robot.getDevice("gps")
gps.enable(timestep)

ruedaIzquierda = robot.getDevice("wheel1 motor")
ruedaDerecha = robot.getDevice("wheel2 motor")
ruedaIzquierda.setPosition(float('inf')) 
ruedaDerecha.setPosition(float('inf'))


def avanzar(vel):
    ruedaIzquierda.setVelocity(vel)
    ruedaDerecha.setVelocity(vel)


def girar(vel):
    ruedaIzquierda.setVelocity(-vel)
    ruedaDerecha.setVelocity(vel)


robot.step(timestep)
startX = gps.getValues()[0]/tilesize
startY = gps.getValues()[2]/tilesize

while robot.step(timestep) != -1:

    x = round( gps.getValues()[0]/tilesize - startX, 1 )
    y = round( gps.getValues()[2]/tilesize - startY, 1 )

    avanzar(1.0)
    
    if (y==-4.0):
        avanzar(0)
        girar(2.0)
    
    print("Imprimo la posicion actual x:", x,"y:", y)
