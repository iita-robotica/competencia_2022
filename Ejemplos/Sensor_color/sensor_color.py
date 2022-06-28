from controller import Robot, Camera # Cargo controlador del robot y la camara

robot = Robot()

colorSensor = robot.getDevice("colour_sensor") # Step 2: Inicializo el sensor de color

timestep = int(robot.getBasicTimeStep())

colorSensor.enable(timestep) # Step 3: Defino la frecuencia de actualizacion del sensor

while robot.step(timestep) != -1:

    image = colorSensor.getImage() # Step 4: Descargo una imagen de la camara

    # Clasifico el codigo de color en RGB
    r = colorSensor.imageGetRed(image, 1, 0, 0)
    g = colorSensor.imageGetGreen(image, 1, 0, 0)
    b = colorSensor.imageGetBlue(image, 1, 0, 0)

    print("r: " + str(r) + " g: " + str(g) + " b: " + str(b))