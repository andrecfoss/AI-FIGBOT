# Inteligência Artificial - Fig-UMa - Phase 1
# IA-FIG-1.py

#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop
from pybricks.parameters import *
from pybricks.robotics import DriveBase

# Import other libraries
import utime
import heapq
import random
import time
import os

ev3 = EV3Brick()    # Initialize the EV3 Brick.

# Initialize the motors.
left_motor = Motor(Port.C)
right_motor = Motor(Port.B)
motorRot= Motor(Port.D)

# Initialize the sensors 
line_sensor = ColorSensor(Port.S2)

# Initialize the drive base.
robot = DriveBase(left_motor, right_motor, wheel_diameter=70, axle_track=131)

# 7X7 Grid: The game itself is played on the 5X5 region of the grid
#10 units = 1cm so each square is 20cm/20cm
position = [[0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0 ,0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0]]

cores = []      # Initializes an array to receive the block colors on the color sensor
indexCores=0

# 0: Unnocupied position on the grid
# 1: Robot Position

# Color blocks index:
# Number 2 (blue block): O (Circle)  
# Number 3 (yellow block): + (Plus) 
# Number 4 (red block): - (Minus)
# Number 5 (green block): X (Cross)

# Other variables
x = 0
y = 0
gyroSensorAngle = 0
moveSpeed = 50
north=1
south=0
east=0
west=0
angle=0
index=0
iteracoesCores=0
pontuacao = 0
tentativas = 0

initial_state = motorRot.angle()

# ______________________________________________________________________

# 
def detect_and_replace_squares2_2(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows - 1):
        for j in range(cols - 1):
            if matrix[i][j] == matrix[i][j + 1] == matrix[i + 1][j] == matrix[i + 1][j + 1] == 2:
                pontuacao += 2**4
                matrix[i][j] = matrix[i][j + 1] = matrix[i + 1][j] = matrix[i + 1][j + 1] = 0

    return matrix

def detect_and_replace_squares_3x3_blocks(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows - 2):
        for j in range(cols - 2):
            if matrix[i][j] == matrix[i][j + 1] == matrix[i][j + 2] == matrix[i + 1][j]  == matrix[i + 1][j + 2] == matrix[i + 2][j] == matrix[i + 2][j + 1] == matrix[i + 2][j + 2] == 2:
                matrix[i][j] = matrix[i][j + 1] = matrix[i][j + 2] = matrix[i + 1][j]  = matrix[i + 1][j + 2] = matrix[i + 2][j] = matrix[i + 2][j + 1] = matrix[i + 2][j + 2] = 0
                pontuacao += 2**8
    return matrix

def detect_and_replace_squares_4x4_blocks(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows - 3):
        for j in range(cols - 3):
            # Verifica se há "1" nos lados do quadrado 4x4
            if matrix[i+3][j] == matrix[i+3][j + 3]==matrix[i][j+3] ==matrix[i][j] == matrix[i][j + 1] == matrix[i][j + 2] == matrix[i + 1][j] == matrix[i + 1][j + 3] == \
               matrix[i + 2][j] == matrix[i + 2][j + 3] == matrix[i + 3][j + 1] == matrix[i + 3][j + 2] == 2:
                # Remove apenas os lados do quadrado 4x4
               matrix[i+3][j] =matrix[i+3][j + 3]=matrix[i][j+3] =matrix[i][j] =matrix[i][j + 1]  = matrix[i][j + 1] = matrix[i][j + 2] = matrix[i + 1][j] = matrix[i + 1][j + 3] = \
               matrix[i + 2][j] = matrix[i + 2][j + 3] = matrix[i + 3][j + 1] = matrix[i + 3][j + 2] = 0
               pontuacao += 2**12  # Atualiza a pontuação para cada conjunto de 8 peças removidas

    return matrix

def detect_and_replace_squares_5x5_sides(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows - 4):
        for j in range(cols - 4):
            # Verifica se há "1" nos lados do quadrado 5x5
            if matrix[i+4][j] == matrix[i+4][j + 4] == matrix[i][j+4] == matrix[i][j] == \
               matrix[i][j + 1] == matrix[i][j + 2] == matrix[i][j + 3] == matrix[i][j + 4] == \
               matrix[i + 1][j] == matrix[i + 1][j + 4] == \
               matrix[i + 2][j] == matrix[i + 2][j + 4] == \
               matrix[i + 3][j] == matrix[i + 3][j + 4] == \
               matrix[i + 4][j + 1] == matrix[i + 4][j + 2] == matrix[i + 4][j + 3] == matrix[i + 4][j + 4] == 2:
                # Remove apenas os lados do quadrado 5x5
                matrix[i+4][j] = matrix[i+4][j + 4] = matrix[i][j+4] = matrix[i][j] = \
                matrix[i][j + 1] = matrix[i][j + 2] = matrix[i][j + 3] = matrix[i][j + 4] = \
                matrix[i + 1][j] = matrix[i + 1][j + 4] = \
                matrix[i + 2][j] = matrix[i + 2][j + 4] = \
                matrix[i + 3][j] = matrix[i + 3][j + 4] = \
                matrix[i + 4][j + 1] = matrix[i + 4][j + 2] = matrix[i + 4][j + 3] = matrix[i + 4][j + 4] = 0
                pontuacao += 2**16  # Atualiza a pontuação para cada conjunto de 16 peças removidas

    return matrix

def detect_and_replace_lines(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows):
        for j in range(cols - 2):
            if matrix[i][j] == matrix[i][j + 1] == matrix[i][j + 2] == 4:
                matrix[i][j] = matrix[i][j + 1] = matrix[i][j + 2] = 0
                pontuacao +=2**3  # Atualiza a pontuação para cada conjunto de três peças removidas
            if matrix[i][j] == matrix[i][j + 1] == 4:
                matrix[i][j] = matrix[i][j + 1] = 0
                pontuacao +=2**2

    return matrix

def remove_crosses(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows-2):
        for j in range(cols-2):
             if matrix[i][j] == matrix[i-1][j]==3 == matrix[i+3][j]== matrix[i+1][j] == matrix[i+2][j] == matrix[i+1][j-1] ==matrix[i+1][j-2] == matrix[i+1][j+1] ==matrix[i+1][j+2]:
                matrix[i][j] = matrix[i-1][j]= matrix[i+3][j]= matrix[i+1][j] = matrix[i+2][j] = matrix[i+1][j-1] =matrix[i+1][j-2] = matrix[i+1][j+1] =matrix[i+1][j+2] =0
                pontuacao += 2**9
             if matrix[i][j] == 3 == matrix[i+1][j] == matrix[i+2][j] == matrix[i+1][j-1] == matrix[i+1][j+1]:
                matrix[i][j] = matrix[i+1][j] = matrix[i+2][j] = matrix[i+1][j-1] = matrix[i+1][j+1] =0
                pontuacao += 2**5
           

    return matrix

def remove_x(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows-3):
        for j in range(cols -3):
            if matrix[i+3][j+3]==matrix[i-1][j+3]==matrix[i+3][j-1]==matrix[i-1][j-1]==matrix[i][j]==5==matrix[i+1][j+1]==matrix[i][j+2]==matrix[i+2][j]==matrix[i+2][j+2]:
                matrix[i+3][j+3]=matrix[i-1][j+3]=matrix[i+3][j-1]=matrix[i-1][j-1]=matrix[i][j]=matrix[i+1][j+1]=matrix[i][j+2]=matrix[i+2][j]=matrix[i+2][j+2]=0
                pontuacao +=2**9
            if matrix[i][j]==5==matrix[i+1][j+1]==matrix[i][j+2]==matrix[i+2][j]==matrix[i+2][j+2]:
                matrix[i][j]=matrix[i+1][j+1]=matrix[i][j+2]=matrix[i+2][j]=matrix[i+2][j+2]=0
                pontuacao +=2**5
       
class Node:
    def __init__(self, x, y, obstacle=False):
        self.x = x
        self.y = y
        self.obstacle = obstacle
        self.g = float('inf')
        self.h = float('inf')
        self.f = float('inf')
        self.parent = None

def heuristic(node, goal):
    return abs(node.x - goal.x) + abs(node.y - goal.y)

def get_neighbors(node, grid):
    neighbors = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Adjacent cells

    for dx, dy in directions:
        x, y = node.x + dx, node.y + dy

        if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and not grid[x][y].obstacle:
            neighbors.append(grid[x][y])

    return neighbors

# _______________________________________________________________________
# A* heuristic algorithm which allows the EV3 to find a path on the grid 
# when detecting a color block with the color sensor.
def a_star(start, goal, grid):
    open_set = []
    closed_set = set()

    start.g = 0
    start.h = heuristic(start, goal)
    start.f = start.g + start.h

    heapq.heappush(open_set, (start.f, id(start), start))

    while open_set:
        current = heapq.heappop(open_set)[2]

        if current == goal:
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1]

        closed_set.add(current)

        for neighbor in get_neighbors(current, grid):
            if neighbor in closed_set:
                continue

            tentative_g = current.g + 1  # Assuming a cost of 1 to move to a neighboring cell

            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = heuristic(neighbor, goal)
                neighbor.f = neighbor.g + neighbor.h

                if not any(node[2] == neighbor for node in open_set):
                    heapq.heappush(open_set, (neighbor.f, id(neighbor), neighbor))

    return None  # No path found

# _______________________________________________________________________

def setGoalNode(goal_x,goal_y):
    print("x rebecido: ", goal_x)
    print("y rebecido: ", goal_y)
    global tentativas
    global index
    global indexCores
    rows, cols = len(position), len(position[0])
    grid = [[Node(i, j, position[i][j] != 0) for j in range(cols)] for i in range(rows)]
    index=0
    motorRot.run_target(20,-120)     #adjust arm movement
    motorRot.run_target(20,0)      
    start_node = grid[0][0]
    goal_node = grid[goal_x][goal_y]
    print(start_node)
    print(goal_node)
    path = a_star(start_node, goal_node, grid)

    if path:
        tentativas=0
        for list in path:
            move_to_position(list[0],list[1])
            index=index+1
        print("--------------")
        for i in position:
            print(i)
        robot.straight(50)
        motorRot.run_target(20,-150)
        robot.straight(-50)
    
        while(index!=0):
            move_to_position(path[index-1][0],path[index-1][1])
            index=index-1
        print("--------------")
        for list2 in position:
            print(list2)
            
       
        if(cores[indexCores]=='Amarelo'):
            position[goal_x][goal_y] = 3
            indexCores=indexCores+1
              
        elif(cores[indexCores]=='Verde'):
            position[goal_x][goal_y] = 5
            indexCores=indexCores+1
                
        elif(cores[indexCores]=='Vermelho'):
            position[goal_x][goal_y] = 4
            indexCores=indexCores+1
            
        elif(cores[indexCores]=='Azul'):
            position[goal_x][goal_y] = 2
            indexCores=indexCores+1
        print("Este é o indexCores:",indexCores)
        print("--------------")
        for list in position:
            print(list)
        return
    else:
        if tentativas<5:
            print("Nao foi possivel obter um caminho")
            defineNumerosAleatorios()
            tentativas=tentativas+1
        else:
            print("Provavelmente não será possivel chegar a mais nenhuma posição")
            return
            

def checkPositions():
    print("-------------")
    for i in position:
        print (i)
    print("-------------")
    remove_crosses(position)
    remove_x(position)
    detect_and_replace_squares_5x5_sides(position)
    detect_and_replace_squares_4x4_blocks(position)
    detect_and_replace_squares_3x3_blocks(position)
    detect_and_replace_squares2_2(position)
    detect_and_replace_lines(position)
    print("-------------")
    for i in position:
        print (i)
    print("-------------")
    print("Pontuação:", pontuacao)
        
def defineNumerosAleatorios():
    random.seed(int.from_bytes(os.urandom(4), 'big'))
    numero1 = random.randint(1, 5)
    numero2 = random.randint(1, 5)
    print(numero1,numero2)
    if(position[numero1][numero2]!=0):
        print("Posicao ocupada, a escolher outra posicao")
        defineNumerosAleatorios()
        
    else:
        setGoalNode(numero1,numero2)
    
print(initial_state)

def turn_to_angle(target_angle, margin_of_error=5, move_speed=50):
    rotate(target_angle)
    
    
def absoluteAngle():                                            #gives the absolute angle which the robot is facing
    global gyroSensorAngle
    if gyroSensorAngle > 360:
        gyroSensorAngle = gyroSensorAngle-360
    if gyroSensorAngle< 0:
        gyroSensorAngle = 360+gyroSensorAngle 

def rotate(after): 
    global angle
    rotation=0
    rotation = after - angle
    absoluteAngle()
    robot.turn(rotation)
    
def teste():
    robot.straight(300)
    robot.turn(180)
   # arm.on_for_rotations(SpeedPercent(75), 0,1)

def movingPath(moveX, moveY):
    movingX = (moveX - x)* 230
    movingY = (moveY - y)* 230
    if (movingX < 0):
        robot.straight(movingX)
    else:
        robot.straight(movingX)
    robot.straight(movingY)

#printPosition()
currentPosition = []           #coordinates in the array position above

def verifyPosition():
    return currentPosition

def detectColour():
    return

def pickBlock():
    verifyPosition()
    #findPath()
    return

def detect_and_print_color(color_sensor):
    # Lê a cor atual do sensor de cor
    global iteracoesCores
    current_color = color_sensor.color()
    

    # Mapeia o valor da cor para o nome correspondente
    while(current_color!=Color.WHITE):
        if current_color == Color.GREEN:
            cores.append('Verde')
            iteracoesCores=iteracoesCores+1
            ev3.speaker.beep()   
            utime.sleep(2)
        if current_color == Color.YELLOW:
            cores.append('Amarelo')
            iteracoesCores=iteracoesCores+1
            ev3.speaker.beep()
            utime.sleep(2) 
        if current_color == Color.BLUE:
            cores.append('Azul')
            iteracoesCores=iteracoesCores+1
            ev3.speaker.beep()
            utime.sleep(2)
        if current_color == Color.RED:
            cores.append('Vermelho')
            iteracoesCores=iteracoesCores+1
            ev3.speaker.beep()
            utime.sleep(2)
       
        current_color = color_sensor.color()
        print(current_color)
    ev3.speaker.beep()
    utime.sleep(0.1)
    ev3.speaker.beep()
    print(cores)

    # Imprime a cor detectada


def agarraBloco():
    detect_and_print_color(line_sensor)
   
# Function which allows the EV3 to move through each square on the grid
# making the necessary movements
def move_to_position(nextX, nextY):
    global x
    global y
    global north
    global east
    global south
    global west

    if (x - nextX) < 0:
        if north == 1:
            turn_to_angle(180)
        elif east == 1:
            turn_to_angle(90)
        elif west == 1:   
            turn_to_angle(-90)
        north, south, east, west = 0, 1, 0, 0
        robot.straight(413) #moving distance between each square on the grid
        x=x+1

    elif (x - nextX) > 0:
        if south == 1:
            turn_to_angle(180)
        elif east == 1:
            turn_to_angle(-90)
        elif west == 1:   
            turn_to_angle(90)
        north, south, east, west = 1, 0, 0, 0
        robot.straight(413) #moving distance between each square on the grid
        x=x-1
        
    elif (y - nextY) > 0:
        if south == 1:
            turn_to_angle(90)
        elif east == 1:
            turn_to_angle(180)
        elif north == 1:   
            turn_to_angle(-90)
        north, south, east, west = 0, 0, 0, 1
      
        robot.straight(413) #moving distance between each square on the grid
        y=y-1

    elif (y - nextY) < 0:
        if south == 1:
            turn_to_angle(-90)
        elif west == 1:
            turn_to_angle(180)
        elif north == 1:   
            turn_to_angle(90)
        north, south, east, west = 0, 0, 1, 0
        robot.straight(413) #moving distance between each square on the grid
        y=y+1


def colorRunning():
    global iteracoesCores
    while iteracoesCores!=0:
        checkPositions()
        defineNumerosAleatorios()
        ev3.speaker.beep()
        iteracoesCores=iteracoesCores-1
        utime.sleep(2)
    checkPositions()
    print("----------------")
    for i in position:
        print(i)
    print("----------------")
    print("Pontuação: ",pontuacao)
        
        
detect_and_print_color(line_sensor)
colorRunning()
motorRot.run_target(20,0) 