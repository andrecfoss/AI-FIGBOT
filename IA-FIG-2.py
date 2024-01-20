#!/usr/bin/env pybricks-micropython

"""
Example LEGO® MINDSTORMS® EV3 Robot Educator Driving Base Program
-----------------------------------------------------------------

This program requires LEGO® EV3 MicroPython v2.0.
Download: https://education.lego.com/en-us/support/mindstorms-ev3/python-for-ev3

Building instructions can be found at:
https://education.lego.com/en-us/support/mindstorms-ev3/building-instructions#robot
"""
#bibliotecas utilizadas 

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop
from pybricks.parameters import *

from pybricks.robotics import DriveBase
import utime
import heapq
import random
import time
import os
# Initialize the EV3 Brick.
ev3 = EV3Brick()

# Initialize the motors.
#motores de movimentacao e rotacao
left_motor = Motor(Port.C)
right_motor = Motor(Port.B)
motorRot= Motor(Port.D)

#extra motors

#estas variaveis sao utilizadas para definir qual metodo sera utilizado na primeira heuristica, uma vez que
# um metodo seja escolhido, esse metodo continuará até o final do jogo
circulogrande=False
vezesGrande=False
cruzGrande=False
bolaMedia=False
heuAlternativa=False

# Initialize the sensors 
#sensor de cor
line_sensor = ColorSensor(Port.S2)
# gyro = GyroSensor(Port.S1)

# Initialize the drive base.
#definicao de variaveis necessarias para fazer do robo preciso e especificar quais motores sao usados para 
# movimentacao
robot = DriveBase(left_motor, right_motor, wheel_diameter=63, axle_track=131)

# gyro.reset_angle(0)
# Go forward and backwards for one meter.
#robot.straight(200)
#ev3.speaker.beep()
#robot.straight(-200)
#ev3.speaker.beep()

# Turn clockwise by 360 degrees and back again.
#robot.turn(360)
#ev3.speaker.beep()

#robot.turn(-360)
#ev3.speaker.beep()

#10 units = 1cm so each square is 20cm/20cm

#Esta é a lista de listas inicial, as colunas representam o Y e as linhas representam o X, basicamente
# 0 significa que está desocupado
# 2 representa a bola
# 3 representa o mais
# 4 representa a linha
# 5 representa o x
position = [[0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0 ,0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0]]

#IMPORTATISSIOMO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# 2 = Bola = Azul
# 3 = mais = Amarelo
# 4 = Linha = Vermelho
# 5 = X = Verde
#IMPORTATISSIOMO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!

cores = [] # Esta lista de cores foi utilizada para a primeira fase, aqui era onde colocávamos as cores ao ler
#Hoje nao fazemos uso desta lista de cores
#este era o indice que utilizavamos para ler as cores na lista de cores
indexCores=0
#0 - unnocupied ; 2 - O blue block; 3 - + yellow block; 4 -  -- red block; 5 - X green block;

#Estes x e y sao as posicoes atuais do robo, ou seja, se o x é 3 e o y é 2, significa que o robo está na posicao
# corresponde a position[3][2]

x = 0
y = 0

# Antes tinhamos o giroscopio instalado, este era a variavel que representava o angulo atual do giroscopio
gyroSensorAngle = 0

# esta variavel era para definir a velocidade do robo, quando estavamos a testar as funcionalidades basicas
# no inicio do projeto
moveSpeed = 50

#Estas variaveis sao muito importantes, elas representam para onde o robo está virado
#north começa a 1 pois o robo começa virado para o norte, e a partir daí vamos gerindo a direção do robo
north=1
south=0
east=0
west=0


index=0

#variavel da pontuacao, é a partir deste que obtemos a pontuacao final
pontuacao = 0

#esta variavel é para dar game over caso o robo tente encontrar muitas vezes o caminho certo, era utilizada
# na primeira fase, por mais que ainda exista, o robo dá game over mesmo antes de chegar a uma quantidade
#de tentativas
tentativas = 0

#esta variavel serve para determinar o tamanho de cada posicao da tabela 7x7, basicamente, onde testámos,
#o quadrado possuia 40 cm, mas fomos testando e este valor, 393, que corresponde a 39,3 cm foi o valor que
#menos nos causou imprecisoes na movimentacao
#tamanho_bloco=5
tamanho_bloco = 393 #valor correto

#estado inicial do motor de rotaçao, ele baiscamente guarda o estado inicial do motor de rotacao
initial_state = motorRot.angle()

#variavel que permite dar um valor de heuristica a uma certa posicao, usado na segunda heuristica
heuristicaValue = 0
#estas variaveis sao utilizadas para a segunda heuristica
#esta lista serve para guardar o valor da grelha que se pretende utilizar na heuristica
grelhaAtual = []
#esta lista vai guardar outras listas contendo os "nodos", ou seja, as possibilidades de tabuleiros 5x5
#com uma certa peça em todas as posicoes vazias
arrayNodos = []  
#esta lista é onde os numeros (cores,figuras) sao armazenados para o robo saber quais sao as cores que foram
#dadas e a sua devida ordem
numeros_gerados=[]

#esta lista guarda o indice de cada arraynodo, de maneira sequencial
arrayNodosIndice = []

#a intencao destas variaveis era para saber qual o x e y, isto é, a posicao da peça que precisa ser inserida
#no tabuleiro, mas foram substituidas por variaveis locais de mais facil acesso
nextX=0
nextY=0

#esta variavel serve para determinar no caso geral da primeira heuristica, qual das peças vao ter prioridade,
#as bolas ou os X, para conseguir formar a figura da bola 3x3 ou formar o X normal
prioridade = False

#esta variavel nao serve para nada, ela basicamente servia para saber quando uma figura foi feita, mas ao
#adotarmos uma nova maneira de fazer a primeira heuristica, ela entrou em desuso, está aqui como resquício
#de uma implementaçao anterior
indexGen = 0


#Heuristica 2

#Esta funcao basicamente atribui a variavel pecaAtual o valor do primeiro elemento da lista dos numeros
#e tambem já remove o primeiro elemento da lista, é usada para atualizar a pecaAtual para que na heuristica
#2 seja possivel usar a peça mais atualizada, tendo em conta que as peças vao sendo removidas a cada vez
#que esta funcao é chamada
def atualizarPecaAtual(arrayBlocos):
    global pecaAtual
    pecaAtual = numeros_gerados.pop(0)

#esta funcao era utilizada para gerar numeros aleatorios, nao foi utilizada com o robo, apenas em uma
#implementacao de uma simulacao do robo para sabermos como o robo reagiria recebendo diversas peças

# def gerar_numeros_aleatorios(arrayBlocos):
#     global numeros_gerados
#     numeros_gerados = arrayBlocos#[random.choice([2, 3, 4, 5]) for _ in range(50)]
#     print(numeros_gerados[1:])

#esta funcao basicamente serve para criar diversos nodos, que sao nada mais que diversas listas que representam
#o tabuleiro 7x7
def grelhaIterada(position, arrayBlocos):                                                 #recebe a grelha atual e a peca a colocar
    #array dos nodos
    global grelhaAtual
    #___________________
    atualizarPecaAtual(arrayBlocos)                                                                #array dos nos
    grelhaAtual = copyGrid(position)                                                    #guarda o estado da grelha atual
    constroiNodos(grelhaAtual)

#esta funcao constroi os nodos todos, ou seja, coloca no arrayNodos, varios nodos, tendo em conta uma grelha
# 7x7, basicamente percorre todas as posicoes do array, e coloca a determinada peça dada ao robo em todas
#as posicoes vazias da grelha atual
def constroiNodos(grelhaAtual):
        global x
        global position
        global pecaAtual
        for i in range(1,len(grelhaAtual)-1):                                           # Itera o array dos nodos, as suas linhas e as suas colunas
            for j in range(1,len(grelhaAtual[i])-1):
                if grelhaAtual[i][j] == 0:
                    grelhaAtual[i][j] = pecaAtual                                       # Altera a posição a 0 para a peça a iterar
                    
                    arrayNodosIndice.append([i,j])
                    arrayNodos.append(grelhaAtual)
                    grelhaAtual = copyGrid(position)                                    #reseta o estado da grelha para o valor que estava antes


#esta funcao é usada para fazer a copia de uma grelha para uma variavel, basicamente, atribui o return desta
#funcao a uma variavel. É utilizada para evitar fazer coisas do tipo, grelha1 = grelha2, onde uma referencia
#de grelha2 é colocada em grelha1, assim, se a grelha1 for modificada, por consequencia a grelha2 também
#será alterada, esta funcao previne isso, passando apenas os valores de maneira independente
def copyGrid(grid):
    return [row[:] for row in grid]                                                     # Cria uma cópia da grelha manualmente


# Função que permite calcular cada valor heuristico de cada posicao de uma certa grelha dado como argumento
# segue um padrao e algumas condições para tornar o valor heuristico de uma certa posicao de uma certa peça
#diferente
def calculaHeuristica(grelha):
    global heuristicaValue
    heuristicaValue = 0

    for i in range(len(grelha)):
        for j in range(len(grelha[i])):


#HEURISTICA PARA POSIÇÕES DE PRIORIDADE PARA CERTAS PEÇAS:
                
# -                              O                                     +                                      x
                
#[0, 5, 5, 5, 0]                 #[40, 45, 35, 15, 10]                 #[0, 5, 10, 5, 0]                      #[10, 5, 25, 5, 40]                            
#[10,15,10,15,10]                #[45, 5, 35, 5, 15]                   #[5, 10, 15, 10, 5]                    #[5, 15, 5, 45, 5]
#[10,10, 5, 10, 10]              #[40, 35, 25, 5, 10]                  #[5, 15, 15, 45, 5]                    #[0, 5, 40, 5, 35]
#[10,15,10,15,10]                #[15, 5, 5, 5, 15]                    #[5, 10, 45, 35, 35]                    #[5, 15, 5, 15, 5]
#[30, 35, 35, 5, 0]              #[10, 15, 10, 15, 10]                 #[0, 5, 10, 35, 0]                      #[10, 5, 0, 5, 10]
                
 #referencias basicas
            arrayHeuristicaMenos = [[0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 5, 5, 5, 0, 0],
                                    [0, 10,15,10,15,10, 0],
                                    [0, 10,10, 5, 10, 10, 0],
                                    [0, 10,15,10,15,10, 0],
                                    [0,30, 35, 35, 5, 0, 0], 
                                    [0, 0, 0, 0, 0, 0, 0]]    
                                                                         
            arrayHeuristicaO = [[0, 0, 0, 0, 0, 0, 0],
                                [0, 45, 45, 35, 15, 10, 0],
                                [0, 45, 5, 35, 5, 15, 0],
                                [0, 40, 35, 25, 5, 10, 0],
                                [0, 15, 5, 5, 5, 15, 0],
                                [0, 10, 15, 10, 15, 10, 0], 
                                [0, 0, 0, 0, 0, 0, 0]]
            
            arrayHeuristicaMais = [[0, 0, 0, 0, 0, 0, 0],
                                   [0, 0, 5, 10, 5, 0, 0],
                                   [0, 5, 10, 15, 10, 5, 0],
                                   [0, 5, 15, 15, 45, 5, 0],
                                   [0, 5, 10, 45, 35, 35, 0],
                                   [0, 0, 5, 10, 35, 0, 0], 
                                   [0, 0, 0, 0, 0, 0, 0]]
            
            arrayHeuristicaCruzes = [[0, 0, 0, 0, 0, 0, 0],
                                     [0, 10, 5, 25, 5, 40, 0],
                                     [0, 5, 15, 5, 45, 5, 0],
                                     [0, 0, 5, 40, 5, 35, 0],
                                     [0, 5, 15, 5, 15, 5, 0],
                                     [0, 10, 5, 0, 5, 10, 0],
                                     [0, 0, 0, 0, 0, 0, 0]]

            #Caso exista apenas números 4 inseridos manualmente na grelha (-)
            if grelha[i][j] == 4:
                if i > 0 and i < 6 and j > 0 and j < 6:
                    if j < 5 and grelha[i][j + 1] == 4:
                        heuristicaValue = heuristicaValue + 50
                    if j > 1 and grelha[i][j - 1] == 4:
                        heuristicaValue = heuristicaValue + 50
                #condicao 2: posicoes favoraveis
                heuristicaValue = heuristicaValue + arrayHeuristicaMenos[i][j]
                         
            # Caso exista apenas números 2 inseridos manualmente na grelha (o)
            elif grelha[i][j] == 2:
                if i > 0 and i < 6 and j > 0 and j < 6:

                    if j < 5 and grelha[i][j+1] == 2:
                        
                         # 2x2: o
                        if i + 1 < len(grelha) and j + 1 < len(grelha[i + 1]) and grelha[i][j + 1] == grelha[i + 1][j] == grelha[i + 1][j + 1] == 2:
                            heuristicaValue = heuristicaValue + 10
                        # 3x3: o
                        if i + 2 < len(grelha) and j + 2 < len(grelha[i + 2]) and grelha[i][j + 1] == grelha[i + 1][j] == grelha[i + 2][j] == grelha[i][j + 2] == grelha[i + 2][j + 2] == 2:
                            heuristicaValue = heuristicaValue + 200
                        # 4x4: o
                        if (grelha[i][j+1] == grelha[i][j + 2] == grelha[i][j + 3] == grelha[i + 1][j] == grelha[i + 2][j] == grelha[i + 3][j] 
                                           == grelha[i + 3][j + 1] == grelha[i + 3][j + 2] == grelha[i + 3][j + 3] == 2):
                            heuristicaValue = heuristicaValue + 250
                        # 5x5: o
                        if (grelha[i][j+1] == grelha[i][j + 2] == grelha[i][j + 3] == grelha[i][j + 4] == grelha[i+1][j] == grelha[i+2][j] == grelha[i+3][j] == grelha[i+4][j]
                                           == grelha[i+4][j+1] == grelha[i+4][j+2] == grelha[i+4][j+3] == grelha[i+4][j+4] 
                                           == grelha[i+1][j+4] == grelha[i+2][j+4] == grelha[i+4][j+4] == grelha[i+4][j+4] == 2):
                            heuristicaValue = heuristicaValue + 400

                #condicao 2: posicoes favoraveis
                heuristicaValue = heuristicaValue + arrayHeuristicaO[i][j]

            # Caso exista apenas números 3 inseridos manualmente na grelha (+)
            elif grelha[i][j] == 3:
                if i > 0 and i < 6 and j > 0 and j < 6:

                    if j < 5 and grelha[i][j+1] == 3:

                        # 3x3: +
                        if i + 2 < len(grelha) and j+2 < len(grelha[i+2]) and grelha[i+1][j] == grelha[i][j+1] == grelha[i-1][j] == grelha[i][j-1] == 3:
                            heuristicaValue = heuristicaValue + 50

                        # 5x5: +
                        if (i + 3 < len(grelha) and j+3 < len(grelha[i+3]) and 
                            grelha[i+1][j] == grelha[i][j+1] == grelha[i-1][j] == grelha[i][j-1] == 
                            grelha[i+2][j] == grelha[i][j+2] == grelha[i-2][j] == grelha[i][j-2] == 3):
                            heuristicaValue = heuristicaValue + 100
                #condicao 2: posicoes favoraveis
                heuristicaValue = heuristicaValue + arrayHeuristicaMais[i][j]

            # Caso exista apenas números 5 inseridos manualmente na grelha (x)
            elif grelha[i][j] == 5:
                if i > 0 and i < 6 and j > 0 and j < 6:

                    if j < 5 and grelha[i][j] == 5:

                        # 3x3: x
                        if i + 2 < len(grelha) and j+2 < len(grelha[i+2]) and grelha[i+1][j+1] == grelha[i-1][j-1] == grelha[i+1][j-1] == grelha[i-1][j+1] == 5:
                            heuristicaValue = heuristicaValue + 50

                        # 5x5: x
                        if (i + 3 < len(grelha) and j+3 < len(grelha[i+3]) and 
                            grelha[i+1][j+1] == grelha[i+2][j+2] == grelha[i-1][j-1] == grelha[i-2][j-2] == 
                            grelha[i-1][j+1] == grelha[i+1][j-1] == grelha[i-2][j+2] == grelha[i+2][j-2] == 5):
                            heuristicaValue = heuristicaValue + 100  
                #condicao 2: posicoes favoraveis
                heuristicaValue = heuristicaValue + arrayHeuristicaCruzes[i][j]          

    return heuristicaValue

def getMaxHeuristica():                              #obtem a iteracao com o maximo valor de heuristica
    global position
    global arrayNodos
    global nextX
    global nextY
    maxHeuristica = 0
    indiceMax = 0
    coordX = 0
    coordY = 0
    for indice, grelha in enumerate(arrayNodos):                                        #cicla o array de nodos e calcula a heuristica de cada nodo
        auxHeur = calculaHeuristica(grelha)
        #print('\nÍndice: '+str(indice+1)+ ' Heurística: '+str(auxHeur))
        #for posicoesAColocar in arrayNodos[indice]:
        #    print (posicoesAColocar)
        
        if (auxHeur>maxHeuristica):
            maxHeuristica = auxHeur
            indiceMax = indice
            for i in range(1,len(grelhaAtual)-1):                                           # Itera o array dos nodos, as suas linhas e as suas colunas
                for j in range(1,len(grelhaAtual[i])-1):
                    if position[i][j] != arrayNodos[indice][i][j]:
                        coordX = i
                        coordY = j                                               #atualiza o position. PODE SER REMOVIDO

    print("\n\n------------RESUMO DA ITERAÇÃO---------------")
    #print("Valor máximo da Heurística obtido:" + str(maxHeuristica))
    #print("Valor do índice com a Heurística máxima:" + str(indiceMax+1))
    print("Coordenadas do novo bloco:")
    print("X:" + str(coordX) + "      Y:" + str(coordY))
    colorRunning(coordX,coordY)
    print("Bloco Colocado: " + str(pecaAtual))
    arrayNodos[indiceMax]=copyGrid(detect_figures(arrayNodos[indiceMax]))
    for j in range(1,6):
        print("[", end='')
        for k in range(1,6):
            if k != 5:
                print(arrayNodos[indiceMax][j][k], end = ',')
            else:
                print(arrayNodos[indiceMax][j][k], end = '')
    
        print ("]")
    position = copyGrid(arrayNodos[indiceMax])
    arrayNodos = []
    print("Pontuação = " + str(pontuacao))

#detecta todas as figuras e remove-as da lista position, adicionando também pontuacao devida para cada figura
#encontrada
def detect_figures(matrix):
    matrix = apaga_line(matrix)
    matrix = apaga_O_5x5(matrix)
    matrix = apaga_O_4x4(matrix)
    matrix = apaga_O_3x3(matrix)
    matrix = apaga_O_2x2(matrix)
    matrix = apaga_cruzes_5x5(matrix)
    matrix = apaga_cruzes_3x3(matrix)
    matrix = apaga_mais_5x5(matrix)
    matrix = apaga_mais_3x3(matrix)
    return matrix

#PARA APAGAR OS OBJETOS
#esta funcao permite apagar as linhas formadas por 2 ou 3 linhas, dando a sua respectiva pontuacao 
# a variavel pontuacao, esta explicadao tambem serve para as outras funcoes seguintes
def apaga_line(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows):
        for j in range(cols - 2):
            if matrix[i][j] == matrix[i][j + 1] == matrix[i][j + 2] == 4:
                matrix[i][j] = matrix[i][j + 1] = matrix[i][j + 2] = 0
                print("\nfigura linha de 3 removida!\n")
                pontuacao +=2**3  # Atualiza a pontuação para cada conjunto de três peças removidas
            elif matrix[i][j] == matrix[i][j + 1] == 4:
                matrix[i][j] = matrix[i][j + 1] = 0
                pontuacao +=2**2
                print("\nfigura linha de 2 removida!\n")

    return matrix

#verifica a bola 2x2
def apaga_O_2x2(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows - 1):
        for j in range(cols - 1):
            if matrix[i][j] == matrix[i][j + 1] == matrix[i + 1][j] == matrix[i + 1][j + 1] == 2:
                pontuacao += 2**4
                matrix[i][j] = matrix[i][j + 1] = matrix[i + 1][j] = matrix[i + 1][j + 1] = 0
                print("\nfigura O 2x2 removida!\n")
    return matrix

#verifica a bola 3x3
def apaga_O_3x3(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows - 2):
        for j in range(cols - 2):
             if matrix[i][j] == matrix[i][j + 1] == matrix[i][j + 2] == matrix[i+1][j]  == matrix[i + 2][j] == matrix[i + 2][j+1] == matrix[i + 2][j + 2] == matrix[i + 1][j + 2] == 2:
                matrix[i][j] = matrix[i][j + 1] = matrix[i][j + 2] = matrix[i+1][j]  = matrix[i + 2][j] = matrix[i + 2][j+1] = matrix[i + 2][j + 2] = matrix[i + 1][j + 2] = 0
                pontuacao += 2**8
                print("\nfigura O 3x3 removida!\n")
    return matrix

#verifica a bola 4x4
def apaga_O_4x4(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(1,rows - 3):
        for j in range(1, cols - 3):
            # Verifica se há "1" nos lados do quadrado 4x4
            if matrix[i][j] == matrix[i+1][j]==matrix[i+2][j] ==matrix[i+3][j] == matrix[i][j + 1] == matrix[i][j + 2] == matrix[i][j+3] == matrix[i + 1][j + 3] == matrix[i + 2][j+3] == matrix[i + 3][j + 3] == matrix[i + 3][j + 1] == matrix[i + 3][j + 2] == 2:
                # Remove apenas os lados do quadrado 4x4
               matrix[i][j] = matrix[i+1][j] = matrix[i+2][j] = matrix[i+3][j] = matrix[i][j + 1] = matrix[i][j + 2] = matrix[i][j+3] = matrix[i + 1][j + 3] = matrix[i + 2][j+3] = matrix[i + 3][j + 3] = matrix[i + 3][j + 1] = matrix[i + 3][j + 2] = 0
               pontuacao += 2**12  # Atualiza a pontuação para cada conjunto de 8 peças removidas
               print("\nfigura O 4x4 removida!\n")
    
    return matrix

#verifica a bola 5x5
def apaga_O_5x5(matrix):
    global pontuacao  # Permite modificar a variável global
    i = 1
    j = 1
            # Verifica se há "2" nos lados do quadrado 5x5
    if (matrix[i][j] == 2 and matrix[i+1][j] == 2 and matrix[i+2][j] == 2 and matrix[i+3][j] == 2 and matrix[i+4][j] == 2 and matrix[i][j + 1] == 2 and matrix[i][j + 2] == 2 and matrix[i][j + 3] == 2 and  matrix[i][j+4] == 2 and matrix[i + 2][j + 4] == 2 and matrix[i + 3][j+4] == 2 and matrix[i + 4][j + 4] == 2 and matrix[i + 1][j+4] == 2 and matrix[i + 4][j + 1] == 2 and  matrix[i + 4][j + 2] == 2 and matrix[i+4][j+3] == 2):
        # Remove apenas os lados do quadrado 5x5
            matrix[i][j] = matrix[i+1][j] = matrix[i+2][j] = matrix[i+3][j] = matrix[i+4][j] = matrix[i][j + 1] = matrix[i][j + 2] = matrix[i][j + 3] =  matrix[i][j+4] = matrix[i + 2][j + 4] = matrix[i + 3][j+4] = matrix[i + 4][j + 4] = matrix[i + 1][j+4] = matrix[i + 4][j + 1] = matrix[i + 4][j + 2] = matrix[i+4][j+3] = 0
            pontuacao += 2**16  # Atualiza a pontuação para cada conjunto de 16 peças removidas
            print("\nfigura O 5x5 removida!\n")
    return matrix
#verifica o X maior
def apaga_cruzes_5x5(matrix):
    global pontuacao  # Permite modificar a variável global
    i = 1
    j = 1
            # Verifica se há "5" nos lados do quadrado 5x5
    if (matrix[i][j] == 5 and matrix[i+1][j+1] == 5 and matrix[i+2][j+2] == 5 and matrix[i+3][j+3] == 5 and matrix[i+4][j+4] == 5 and matrix[i+4][j] == 5 and matrix[i+3][j + 1] == 5 and  matrix[i+1][j+3] == 5 and matrix[i][j + 4] == 5):
        # Remove apenas os lados do quadrado 5x5
            matrix[i][j] = matrix[i+1][j+1] = matrix[i+2][j+2] = matrix[i+3][j+3] = matrix[i+4][j+4] = matrix[i+4][j] = matrix[i+3][j + 1] =  matrix[i+1][j+3] = matrix[i][j + 4] = 0
            pontuacao += 2**9  # Atualiza a pontuação para cada conjunto de 9 peças removidas
            print("\nfigura X 5x5 removida!\n")
    return matrix
#verifica o X normal
def apaga_cruzes_3x3(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows - 2):
        for j in range(cols - 2):
             if matrix[i][j] == matrix[i+1][j + 1] == matrix[i+2][j+2] == matrix[i+2][j]  == matrix[i][j+2] == 5:
                matrix[i][j] = matrix[i+1][j + 1] = matrix[i+2][j+2] = matrix[i+2][j]  = matrix[i][j+2] = 0
                pontuacao += 2**5
                print("\nfigura X 3x3 removida!\n")
    return matrix

#verifica o mais normal
def apaga_mais_3x3(matrix):
    global pontuacao

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows - 2):
        for j in range(cols - 2):

            if (matrix[i][j+1] == 3 and matrix[i+1][j] == 3 and matrix[i+1][j+1] == 3 and matrix[i+1][j+2] == 3 and matrix[i+2][j+1] == 3):

                matrix[i][j+1] = matrix[i+1][j] = matrix[i+1][j+1] = matrix[i+1][j+2] = matrix[i+2][j+1] = 0
                pontuacao += 2**5
                print("\nfigura + 3x3 removida\n")

    return matrix

#verifica o mais (+) grande
def apaga_mais_5x5(matrix):
    global pontuacao
    i = 1
    j = 1

    if (matrix[i][j+2] == 3 and matrix[i+1][j+2] == 3 and matrix[i+2][j+2] == 3 and matrix[i+3][j+2] == 3 and matrix[i+4][j+2] == 3 
                            and matrix[i+2][j] == 3 and matrix[i+2][j+1] == 3 and matrix[i+2][j+3] == 3 
                            and matrix[i+2][j+4] == 3):
        
        matrix[i][j+2] = matrix[i+1][j+2] = matrix[i+2][j+2] = matrix[i+3][j+2] = matrix[i+4][j+2] = matrix[i+2][j] = matrix[i+2][j+1] = matrix[i+2][j+3] = matrix[i+2][j+4] = 0
        pontuacao += 2**9
        print("\nfigura + 5x5 removida!\n")

    return matrix

#esta funcao é a funcao utilizada para chamar as funcoes necessarias para fazer a segunda heuristica
# ser executada com sucesso
def segundaHeuristica(matrix, arrayNumerosGerados):
    while arrayNumerosGerados:

        print (numeros_gerados[1:])
        grelhaIterada(matrix, arrayNumerosGerados)
        getMaxHeuristica()
        print("\n\n\n")
    print("Fim do programa. :) \n")
    removePontuacao=0
    for i in position:
        for j in i:
            if position[i][j]!=0:
                removePontuacao+=1
    pontuacao=pontuacao-(2**removePontuacao)
    print("Pontuacao :" + str(pontuacao))





#estas funcoes permitem verifica figuras, assim como as anteriores, os nomes estao 
# diferentes pois foram feitas por pessoas diferentes e tambem sao utilizada em heuristicas diferentes
#lembrando que assim como as outras, estas também apagam da lista Position e incrementam a pontuacao necessarias
# para a figura terminada com sucesso
#detecta a bola2x2
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

#detecta a bola 3x3
def detect_and_replace_squares_3x3_blocks(matrix):
    global pontuacao  # Permite modificar a variável global
    global indexGen
    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows - 2):
        for j in range(cols - 2):
            if matrix[i][j] == matrix[i][j + 1] == matrix[i][j + 2] == matrix[i + 1][j]  == matrix[i + 1][j + 2] == matrix[i + 2][j] == matrix[i + 2][j + 1] == matrix[i + 2][j + 2] == 2:
                matrix[i][j] = matrix[i][j + 1] = matrix[i][j + 2] = matrix[i + 1][j]  = matrix[i + 1][j + 2] = matrix[i + 2][j] = matrix[i + 2][j + 1] = matrix[i + 2][j + 2] = 0
                pontuacao += 2**8
                contaXeBola(2)
                indexGen=0
    return matrix

#detecta a bola 4x4
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

#detecta a bola 5x5
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
                pontuacao += 16  # Atualiza a pontuação para cada conjunto de 16 peças removidas

    return matrix           

#detecta as linhas
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

#detecta os mais (+)
def remove_crosses(matrix):
    global pontuacao  # Permite modificar a variável global

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows-3):
        for j in range(cols-3):
            if matrix[i][j] == matrix[i-1][j]==3 == matrix[i+3][j]== matrix[i+1][j] == matrix[i+2][j] == matrix[i+1][j-1] ==matrix[i+1][j-2] == matrix[i+1][j+1] ==matrix[i+1][j+2]:
                matrix[i][j] = matrix[i-1][j]= matrix[i+3][j]= matrix[i+1][j] = matrix[i+2][j] = matrix[i+1][j-1] =matrix[i+1][j-2] = matrix[i+1][j+1] =matrix[i+1][j+2] =0
                pontuacao += 2**9
    for i in range(rows-2):
        for j in range(cols-2):        
            if matrix[i][j] == 3 == matrix[i+1][j] == matrix[i+2][j] == matrix[i+1][j-1] == matrix[i+1][j+1]:
                matrix[i][j] = matrix[i+1][j] = matrix[i+2][j] = matrix[i+1][j-1] = matrix[i+1][j+1] =0
                pontuacao += 2**5
           

    return matrix

#detecta os X
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
                contaXeBola(1)


#esta funcao é utilizada para colocar  o numero 5 em uma posicao de lixo, de discarte, era utilizada 
#em um bloco de codigo a parte, quando a primeira heuristica foi implementada, neste caso preciso
# a parte que rege o caso geral da heuristica 1
#ela basicamente verifica onde estao os 6's da lista de listas position, e coloca o valor 5 nessa posicao
#ela sequer está adaptada para ser usada com o robo, visto que muda diretamente a posicao, metodo este que 
#nao funciona com o robo. Ela verifica onde estao os 6's da lista pois numa anterior implementacao, nos tinhamos
# nas posicoes de descarte, o numero 6 para as identificar, tornando assim as coisas mais dinamicas, mas acabamos
# por modificar pois isso interfere diretamente na composicao da lista de listas position, o que costumava
#dar erros
def coloca5novazio():
    for i in range(len(position)):
        for j in range(len(position[0])):
            if position[i][j] == 6:
                position[i][j] = 5
                opcao_2()
                return
    print("Não foi encontrado nenhum valor 6 na matriz.")

#esta funcao faz exatamente o que a de cima faz, só que ao invés de colcoar o numero 5 coloca o numero 2
def coloca2novazio():
    for i in range(len(position)):
        for j in range(len(position[0])):
            if position[i][j] == 6:
                position[i][j] = 2
                opcao_2()
                return True
    print("Não foi encontrado nenhum valor 6 na matriz.")
    return False

#esta funcao é a funcao substituta para colocar peças em uma posicao de descarte e está adaptada para o robo
#o que ela traz de retorno é a posicao especifica onde a peça será levada, e ficará lá até o final do jogo
def colocaNumeronoVazio(numero):
     for i in range(len(position)):
        for j in range(len(position[0])):
            if position[1][4]==0:

                opcao_2()
                return [1,4]
            if position[5][5]==0:

                opcao_2()
                return [5,5]
            if position[2][5]==0:
                opcao_2()
                return [2,5]
            if position[4][2]==0:

                opcao_2()
                return [4,2]
            if position[4][1]==0:

                opcao_2()
                return [4,1]
     return [-1,-1]
    
#esta funcao foi feita para identificar quantos + e X apareciam na lista de blocos, até aparecer a décima
#sexta bola, usada para fazer uma bola 5x5, basicamente, através dele sabemos a soma de X e +, podendo ser
#utilizada para condicionar a utilizacao do metodo da primeira heuristica que permite fazer uma bola
#5x5
def containstancias_de_2():
    global prioridade
    global indexGen

    count_3 = 0
    count_5 = 0
    count_2 = 0

    for numero in numeros_gerados:
        if numero == 3:
            count_3 += 1
        elif numero == 5:
            count_5 += 1
        elif numero == 2:
            count_2 += 1

            if count_2 == 16:
                break  # Stop counting after the 16th occurrence of 2
    return count_3 + count_5

#faz o mesmo que a funcao de cima porem, ao inves de ser para a bola 5x5, é para a bola 4x4 
def containstancias_de_2_2():
    global prioridade
    global indexGen

    count_3 = 0
    count_5 = 0
    count_2 = 0

    for numero in numeros_gerados:
        if numero == 3:
            count_3 += 1
        elif numero == 5:
            count_5 += 1
        elif numero == 2:
            count_2 += 1

            if count_2 == 12:
                break  # Stop counting after the 12th occurrence of 2
    return count_3 + count_5

#esta funcao conta quantos 2 e 4 aparecem, isto é, quantas bolas e quantas linhas aparecem 
# até a formacao de um X grande, é usada para saber se a bola grande deve ser feita, ou daria game over caso
#tentasse faze-la
def contaMaisEBola():
    contaDois=0
    contaTres=0
    contaCinco=0
    for i in numeros_gerados:
        if i==2:
            contaDois+=1
        elif i==3:
            contaTres+=1
        elif i==5:
            contaCinco+=1
            if contaCinco==9:
                break
    return contaDois + contaTres

#esta variavel conta e retorna quantas vezes o numero dado como argumento aparece dentro da matriz, é utilizado
# para definir metodos dentro da primeira heuristica, por exemplo.
def contar_ocorrencias_matriz(numero):
    count_numero = 0
    for i in range(len(position)):
        for j in range(len(position[0])):
            if position[i][j] == numero:
                count_numero += 1
    return count_numero

#conta e devolve as ocorrencias de um certo valor dentro da lista de blocos fornecidos no inicio 
def contar_ocorrencias_(n):
    global numeros_gerados
    if not numeros_gerados:
        gerar_numeros_aleatorios()
    return numeros_gerados.count(n)


    #detect_and_replace_squares2_2(position)
   # opcao_2()
   
#conta e devolve as ocorrencias de um certo valor dentro da lista de blocos fornecidos no inicio 
def contar_ocorrencias_numero(numero):
    return numeros_gerados.count(numero)
         
#esta funcao é responsável por determinar qual das duas figuras vao ter prioridade no caso geral da primeira
# heuristica, isto é, se a prioridade for True significa que a bola 3x3 tem prioridade, caso contrario 
# é o X que possui prioridade
#Esta funcao conta, verificando tanto na lista como na grelha, qual das duas figuras vai ser feita primeiro
#a bola 3x3 ou o X normal, e define uma prioridade
def contaXeBola(figura):
    #1 - remove x, 2- - remove O
    global prioridade
    contaBolaNaMatriz=0
    contaXNaMatriz=0
    contaBola=0
    contaX=0

    if position[1][5]==5:
        contaX+=1
        contaXNaMatriz+=1
    if position[3][5]==5:
        contaX+=1
        contaXNaMatriz+=1
    if position[2][4]==5:
        contaX+=1
        contaXNaMatriz+=1
    if position[3][3]==5:
        contaX+=1
        contaXNaMatriz+=1
    if position[1][3]==5:
        contaX+=1
        contaXNaMatriz+=1

    if position[3][3]==2:
        contaBola+=1
        contaBolaNaMatriz+=1
    if position[1][3]==2:
        contaBola+=1
        contaBolaNaMatriz+=1
    if position[1][1]==2:
        contaBola+=1
        contaBolaNaMatriz+=1
    if position[2][1]==2:
        contaBola+=1
        contaBolaNaMatriz+=1
    if position[3][1]==2:
        contaBola+=1
        contaBolaNaMatriz+=1
    if position[3][2]==2:
        contaBola+=1
        contaBolaNaMatriz+=1
    if position[1][2]==2:
        contaBola+=1
        contaBolaNaMatriz+=1
    if position[2][3]==2:
        contaBola+=1
        contaBolaNaMatriz+=1




    for i in numeros_gerados:
        
        if i==2:
            contaBola+=1
        elif i==5:
            contaX+=1
        if contaX==5:
            prioridade=False
            break
        elif contaBola==8:
            prioridade=True
            break
        
    print("Bolas: "+str(contaBola))
    print("X: "+str(contaX))
    if figura==5:
        return contaBola
    elif figura==6:
        return contaX
    elif figura==7:
        return contaXNaMatriz
    elif figura==8:
        return contaBolaNaMatriz
    return
    

#esta funcao é responsável por fazer ou dar continuidade ao metodo geral da primeira heuristica, no que se refere a 
#circulos, é aqui que ele decide se vai fazer a bola 3x3, a bola 2x2, se vai descartar um bloco
#A prioridade sendo True, significa que a bola 3x3 pode ser finalizada sem problemas
#A prioridade nao sendo true, significa que todas as posicoes especificas para formar a bola 3x3 podem ser preenchidas
#com excecao daquelas posicoes que vao ser usada para fazer o X normal
#se nao possuir peças suficientes para uma bola de 3x3, faz uma 2x2
def opcao_escolheCirculos():
    global numero_circulos
    auxPosicao2=[-1,-1]
    global prioridade
    mostra_nuemeros_aleatorios()
    print("Numero de ciruclos é :"+str(contar_ocorrencias_numero(2)))
    contaXeBola(5)
    
    if(prioridade==True and contaXeBola(5)==8):
        #sequencia determinada por nós para que as posicoes sejam colocadas de maneira eficiente, dando
        #prioriade as posicoes que podem dar conflito com o X
        if position[3][3]==0:
            auxPosicao2=[3,3]
        elif position[1][3]==0:
            auxPosicao2=[1,3]
        elif position[3][2]==0:
            auxPosicao2=[3,2]
            
        elif position[3][1]==0:
            auxPosicao2=[3,1]
            
        elif position[1][2]==0:
            auxPosicao2=[1,2]
            
        elif position[1][1]==0:
            auxPosicao2=[1,1]
            
        elif position[2][3] == 0:
            auxPosicao2=[2,3]
        
        elif position[2][1]==0:
            auxPosicao2=[2,1]
            
        numeros_gerados.pop(0)
        detect_and_replace_squares2_2(position)
        detect_and_replace_squares_3x3_blocks(position)
        
        opcao_2()
        return auxPosicao2
    elif(prioridade==False and (contar_ocorrencias_numero(2)+contar_ocorrencias_matriz(2))>=8):
        if position[3][2]==0:
            auxPosicao2=[3,2]
            
        elif position[3][1]==0:
            auxPosicao2=[3,1]
        
        elif position[1][2]==0:
            auxPosicao2=[1,2]
            
        elif position[1][1]==0:
            auxPosicao2=[1,1]
        
        elif position[2][3] == 0:
            auxPosicao2=[2,3]
        
        elif position[2][1]==0:
            auxPosicao2=[2,1]
            

        numeros_gerados.pop(0)
        detect_and_replace_squares2_2(position)
        detect_and_replace_squares_3x3_blocks(position)
        
        opcao_2()
        return auxPosicao2
    elif(contar_ocorrencias_numero(2)+contar_ocorrencias_matriz(2)<8):

        if position[2][2]==0:
            auxPosicao2=[2,2]
        elif position[2][1]==0:
            auxPosicao2=[2,1]
        elif position[1][2]==0:
            auxPosicao2=[1,2]
        elif position[1][1]==0:
            auxPosicao2 = [1,1]
        
        numeros_gerados.pop(0)
        detect_and_replace_squares2_2(position)
        detect_and_replace_squares_3x3_blocks(position)
        
        opcao_2()
        return auxPosicao2
    else:
        auxPosicao2=colocaNumeronoVazio(2)
        numeros_gerados.pop(0)
        opcao_2()
        return auxPosicao2
    return auxPosicao2


#Assim como a funcao de cima, esta também serve para o caso geral da primeira heuristica, contém a sequencia
#e logica de colocacao de peças X, em posicoes especificar, lembrando que no caso da prioridade ser False,
#significa que o X tem prioridade para fazer o seu X normal
def opcao_escolhevezes():
    
    auxPosicao2=[-1,-1]
    global prioridade
    global numero_vezes
    mostra_nuemeros_aleatorios()
    contaXeBola(1)
    print("Numero de x é :"+str(contar_ocorrencias_numero(5)))
    if numeros_gerados:
        print("Existe numeros aleatorios")
        if(numeros_gerados[0]==5):
        
            if(prioridade==False and position[3][3]==0 and contaXeBola(6)==5):

               auxPosicao2=[3,3]
               remove_x(position)
               numeros_gerados.pop(0)
               opcao_2()
               return auxPosicao2
            if(prioridade==False and position[1][3]==0 and contaXeBola(6)==5):

                auxPosicao2=[1,3]
                remove_x(position)
                numeros_gerados.pop(0)
                opcao_2()
                return auxPosicao2
            if(position[1][5]==0):

               auxPosicao2=[1,5]
               numeros_gerados.pop(0)
               remove_x(position)
               opcao_2()
               
               return auxPosicao2
            if(position[2][4]==0):

               auxPosicao2=[2,4]
               numeros_gerados.pop(0)
               remove_x(position)
               opcao_2()
               return auxPosicao2
            if(position[3][5]==0):

               auxPosicao2=[3,5]
               numeros_gerados.pop(0)
               remove_x(position)
               opcao_2()
               return auxPosicao2
            if((position[1][3]in(0,2,22) and position[3][3] in (0,2,22) and contar_ocorrencias_numero(5)==1)):
                auxPosicao2=colocaNumeronoVazio(5)
                
                numeros_gerados.pop(0)
                opcao_2()
                return auxPosicao2
            if(position[1][3]in(2,22) and position[3][3] in (2,22)):
                auxPosicao2=colocaNumeronoVazio(5)
                numeros_gerados.pop(0)
                opcao_2()
                return auxPosicao2

        else:
            print("O numero não é um x")
    
    else:
        print("Não existe numeros aleatoriso")
        
#Assim como a funcao de cima, esta também serve para o caso geral da primeira heuristica, possui a sequencia
# da colocacao de peças de +, de uma maneira que ela nunca fique travada, pois sempre existe um caminho para colocar
#a proxima peça
def opcao_escolhemais():
    global numero_mais
    auxPosicao2=[-1,-1]
    mostra_nuemeros_aleatorios()
    numero_mais = contar_ocorrencias_numero(3)
    print("Numero de + é :"+str(contar_ocorrencias_numero(3)))
    if numeros_gerados:
        print("existe numeros gerados")
        if numeros_gerados[0]==3:
            print("O primeiro indice é um +")
            if position[3][4] == 0:
               auxPosicao2=[3,4]
               remove_crosses(position)
               numeros_gerados.pop(0)
               opcao_2()
               return auxPosicao2
            if position[4][3]==0:

               auxPosicao2=[4,3]
               remove_crosses(position)
               numeros_gerados.pop(0)
               opcao_2()
               return auxPosicao2
            if position[4][4]==0:

               auxPosicao2=[4,4]
               remove_crosses(position)
               numeros_gerados.pop(0)
               opcao_2()
               return auxPosicao2
            if position[5][4]==0:

               auxPosicao2=[5,4]
               remove_crosses(position)
               numeros_gerados.pop(0)
               opcao_2()
               return auxPosicao2
            if position[4][5]==0:

               auxPosicao2=[4,5]
               remove_crosses(position)
               numeros_gerados.pop(0)
               opcao_2()
               return auxPosicao2
            
        else:
            print("Nao existe nenhum +")
            
    else:
        print("Nao existe numeros gerados")
        return auxPosicao2

#2 - Azul - Circulo
#3 - Amarelo - Cruz
#4 - Vermelho - Linha
#5 - Verde - X

#Esta funcao permite fazer, na heuristica 1, a bola 5x5, detém a sequencia de onde os numeros serao colocados
#e onde outros numeros serao descartados
def opcaoescolhemaior(escolha):
    global escolhemaior
    global numero_linhas
    auxP=[-1,-1]
    numero_linhas = contar_ocorrencias_numero(4)
    mostra_nuemeros_aleatorios()
    #sequencias das bolas
    if(numeros_gerados[0]==2):
        if position[1][1]==0:
            auxP=[1,1]
        elif position[1][2]==0:
            auxP=[1,2]
        elif position[1][3]==0:
            auxP = [1,3]
        elif position[1][4]==0:
            auxP = [1,4]
        elif position[1][5]==0:
            auxP = [1,5]
        elif position[2][5]==0:
            auxP = [2,5]
        elif position[3][5]==0:
            auxP = [3,5]
        elif position[4][5]==0:
            auxP = [4,5]
        elif position[5][5]==0:
            auxP = [5,5]
        elif position[2][1]==0:
            auxP = [2,1]
        elif position[3][1]==0:
            auxP = [3,1]
        elif position[4][1]==0:
            auxP = [4,1]
        elif position[5][1]==0:
            auxP = [5,1]
        elif position[5][2]==0:
            auxP = [5,2]
        elif position[5][4]==0:
            auxP = [5,4]
        elif position[5][3]==0:
            auxP = [5,3]
        detect_and_replace_squares_5x5_sides(position)
        
        auxP.append(2)
        
             

        numeros_gerados.pop(0)
        opcao_2()
        return auxP
    #sequencia dos menos
    elif(numeros_gerados[0]==4):
        if contar_ocorrencias_numero(4)==1 and position[4][2]==4 and position[4][4]==0:
            auxP = [4, 3]
        elif position[4][2]==0:
            auxP = [4, 2]
        elif position[4][4]==0:
            auxP = [4, 4]
        elif position[4][3]==0:
            auxP = [4, 3]
        detect_and_replace_lines(position)
        auxP.append(4)
    #caso sejam + ou x, serao descartados
    elif(numeros_gerados[0]!=4 and numeros_gerados[0]!=2):
        if position[2][2]==0:
            auxP = [2, 2]
        elif position[2][4]==0:
            auxP = [2, 4]
        elif position[2][3]==0:
            auxP = [2, 3]
        elif position[3][2]==0:
            auxP = [3, 2]
        elif position[3][4]==0:
            auxP = [3, 4]
        elif position[3][3]==0:
            auxP = [3, 3]
        elif position[4][4]==0:
            auxP = [4, 4]
        auxP.apprend(numeros_gerados[0])    

        
    numeros_gerados.pop(0)
    opcao_2()
    return auxP
   # elif(numeros_gerados[0]==5):
   #    if(position[][]==0)

#esta funcao permite colocar as linhas da maneira pretendida para o caso geral da primeira heuristica
def opcao_escolheLinhas1():
    auxPosicao2=[-1,-1]
    global numero_linhas
    mostra_nuemeros_aleatorios()
    numero_linhas = contar_ocorrencias_numero(4)
    print("Numero de linhas :" + str(contar_ocorrencias_numero(4)))

    if numeros_gerados and numeros_gerados[0] == 4:
        print("O numero na primeira posição é um 4")

        if(position[5][1] == 4 and position[5][3]==4):
            auxPosicao2 = [5,2]
            numeros_gerados.pop(0)
            detect_and_replace_lines(position)  # Adicione esta linha
            opcao_2()
            return auxPosicao2

        if(position[5][1] == 0 and position[5][2] == 0 and position[5][3] == 0):

            auxPosicao2 = [5,1]
            numeros_gerados.pop(0)
            detect_and_replace_lines(position)  # Adicione esta linha
            opcao_2()
            return auxPosicao2

        if(position[5][1] == 4 and position[5][3] == 0 and contar_ocorrencias_numero(4) >= 2):
            auxPosicao2 = [5,3]
            numeros_gerados.pop(0)
            detect_and_replace_lines(position)  # Adicione esta linha
            opcao_2()
            return auxPosicao2

        if(contar_ocorrencias_(4) == 1):
            auxPosicao2 = [5,2]
            numeros_gerados.pop(0)
            detect_and_replace_lines(position)  # Adicione esta linha
            opcao_2()
            return auxPosicao2
    else:
        print("O numero não é um 4 ou números_gerados não existe primeiro clicar opcao 1 que gera numeros ")
    return auxPosicao2

#esta funcao foi utilizada para criar uma sequencia de numeros aleatorios para a lista de numeros gerados
#apenas utilizada na fase de testes
def opcao_1():
    gerar_numeros_aleatorios()
    mostra_nuemeros_aleatorios()
    print("Numero de circulos é :"+str(contar_ocorrencias_numero(2)))
    return

#esta funcao é a funcao responsável por fazer o X maior para a primeira heuristica, nele possui a 
#sequencia de onde os X devem ser colocados, outras peças que serao descartadas e figuras formadas, neste caso
#as linhas também serao formada
def opcaoescolhemaiorvezes():
    auxPosicao=[-1,-1]
    #caso seja um X, forma nesta sequencia
    if numeros_gerados[0]==5:
        if position[3][3]==0:
            auxPosicao=[3,3,5]
            
        elif position[2][2]==0:
            auxPosicao=[2,2,5]
            
        elif position[4][2]==0:
            auxPosicao=[4,2,5]
            
        elif position[4][4]==0:
            auxPosicao=[4,4,5]
        
        elif position[1][1]==0:
            auxPosicao=[1,1,5]
            
        elif position[5][1]==0:
            auxPosicao=[5,1,5]
            
        elif position[5][5]==0:
            auxPosicao=[5,5,5]
            
            
        elif position[1][5]==0:
            auxPosicao=[1,5,5]
            
        
        elif position[2][4]==0:
            auxPosicao=[2,4,5]
        
        return auxPosicao
    #se nao é X nem linha, vao para posicoes de descarte, seguindo esta sequencia
    elif numeros_gerados[0]!=4 and numeros_gerados[0]!=5:
        if position[2][1]==0:
            auxPosicao=[2,1,numeros_gerados[0]]
        elif position[3][1]==0:
            auxPosicao=[3,1,numeros_gerados[0]]
            
        elif position[4][1]==0:
            auxPosicao=[4,1,numeros_gerados[0]]
        elif position[2][5]==0:
            auxPosicao=[2,5,numeros_gerados[0]]
        elif position[3][5]==0:
            auxPosicao=[3,5,numeros_gerados[0]]
            
        elif position[4][5]==0:
            auxPosicao=[4,5,numeros_gerados[0]]
            
        elif position[1][2]==0:
            auxPosicao=[1,2,numeros_gerados[0]]
        elif position[1][4]==0:
            auxPosicao=[1,4,numeros_gerados[0]]
            
    #caso sejam linhas
    elif numeros_gerados(0)==4:
        
        if position[5][2]==0:
            auxPosicao=[5,2,4]
        elif position[5][4]==0 and contar_ocorrencias_numero(4)>=2:
            auxPosicao=[5,4,4]
        elif position[5][3]==0:
            auxPosicao=[5,3,4]
            
            
            
    numeros_gerados.pop(0)
    detect_and_replace_lines(position)
    remove_x(position)
    opcao_2()
    return auxPosicao

#esta funcao esta responsavel por fazer o mais (+) grande, é nela que há a sequencia pela qual os + precisam ser preenchidos
#assim como ele conseguira formar as bolas 2x2 e tambem linhas 2x2
#além disso, tambem indica onde as peças serao descartadas, neste caso, esta funcao descarta sem chance de
#formar figura, as peças X 
def opcaocruzGrande():
    auxPosicao=[-1,-1]
    #caso seja +, preenche nesta sequencia
    if numeros_gerados[0]==3:
        if position[3][2]==0:
            auxPosicao=[3,2,3]
            
            
        elif position[3][4]==0:
            auxPosicao=[3,4,3]
            
        elif position[3][3]==0:
            auxPosicao=[3,3,3]
            
        elif position[4][3]==0:
            auxPosicao=[4,3,3]
            
        elif position[3][1]==0:
            auxPosicao=[3,1,3]
            
        elif position[5][3]==0:
            auxPosicao=[5,3,3]
            
            
        elif position[3][5]==0:
            auxPosicao=[3,5,3]
            
        elif position[1][3]==0:
            auxPosicao=[1,3,3]
            
        elif position[2][3]==0:
            auxPosicao=[2,3,3]
            
    #caso seja uma bola, conseguira fazer a 2x2
    elif numeros_gerados[0]==2:
        if position[4][2]==0:
            auxPosicao=[4,2,2]
            
        elif position[4][1]==0:
            auxPosicao=[4,1,2]
            
        elif position[5][2]==0:
            auxPosicao=[5,2,2]
            
        elif position[5][1]==0:
            auxPosicao=[5,1,2]
        
    #caso seja uma linha, sera colocada nestas 2 posicoes
    elif numeros_gerados[0]==4:
        if position[1][4]==0:
            auxPosicao=[1,4,4]
            
        elif position[1][5]==0:
            auxPosicao=[1,5,4]
    
    #caso seja um X, tera de ser descartada para estas posicoes seguintes
    elif numeros_gerados[0]==5:
        if position[1][1]==0:
            auxPosicao=[1,1,5]
            
        elif position[1][2]==0:
            auxPosicao=[1,2,5]
            
        elif position[2][1]==0:
            auxPosicao=[2,1,5]
            
        elif position[2][2]==0:
            auxPosicao=[2,2,5]
        
        elif position[4][4]==0:
            auxPosicao=[4,4,5]
            
        elif position[5][5]==0:
            auxPosicao=[5,5,5]
            
        elif position[4][5]==0:
            auxPosicao=[4,5,5]
            
        elif position[5][4]==0:
            auxPosicao=[5,4,5]
            
    detect_and_replace_squares2_2(position)
    detect_and_replace_lines(position)
    remove_crosses(position)
    numeros_gerados.pop(0)
    opcao_2()
    return auxPosicao
    
#esta funcao é responsavel por fazer a bola 4x4 na primeira heuristica, basicamente, descarta tudo menos linhas e bolas
def opcaoBolaMedia():
    auxP=[-1,-1]
    #caso seja uma bola, é preenchida nesta sequencia
    if numeros_gerados[0]==2:
        if position[4][4]==0:
            auxP=[4,4]
            
        elif position[4][3]==0:

            auxP=[4,3]
        
        
        elif position[3][4]==0:

            auxP=[3,4]
        
        elif position[2][4]==0:

            auxP=[2,4]
        
        elif position[1][1]==0:
            auxP=[1,1]
            
        elif position[1][2]==0:
            auxP=[1,2]
            
        elif position[1][3]==0:
            auxP=[1,3] 
             
        elif position[1][4]==0:
            auxP=[1,4]
             
        elif position[3][1]==0:
            auxP=[3,1]  
            
            
        elif position[4][1]==0:
            auxP=[4,1]  
        
        elif position[2][1]==0:
            auxP=[2,1]
        elif position[4][2]==0:
            auxP=[4,2]
        
        auxP.append(2)
        
    #caso seja uma linha, sera preenchida nesta sequencia
    elif numeros_gerados[0]==4:
        if (contar_ocorrencias_numero(4)==1 and position[5][1]==4 and position[5][3]==4) or (contar_ocorrencias_numero(4)==2 and position[5][1]==4) or contar_ocorrencias_numero(4)>2:
            
            if position[5][1]==0:
                auxP=[5,1]
                
            elif position[5][3]==0:
                auxP=[5,3]
                
            elif position[5][2]==0:
                auxP=[5,2]
                
            auxP.append(4)
        elif contar_ocorrencias_numero(4)==1 and position[5][3]!=4:
            auxP=[5,2]
            auxP.append(4)
        
    #se nao for bola nem linha, sera descartada nesta ordem
    elif numeros_gerados[0]!=2 and numeros_gerados[0]!=4:
        if position[1][5]==0:
            auxP=[1,5]
            
        elif position[2][5]==0:
            auxP=[2,5]
            
        elif position[3][5]==0:
            auxP=[3,5]
            
        elif position[4][5]==0:
            auxP=[4,5]
            
        elif position[5][5]==0:
            auxP=[5,5]
            
        elif position[5][4]==0:
            auxP=[5,4]
            
        elif position[3][3]==0:
            auxP=[3,3]
            
        elif position[3][2]==0:
            auxP=[3,2]
            
        elif position[2][3]==0:
            auxP=[2,3]
            
        elif position[2][2]==0:
            auxP=[2,2]
            
        auxP.append(numeros_gerados[0])
            
    detect_and_replace_squares_4x4_blocks(position)
    detect_and_replace_lines(position)
    numeros_gerados.pop(0)
    opcao_2()
    return auxP

#esta funcao é responsavel por, detectar figuras, determinar quais metodos da primeira heuristica serao utili
#zados, remover da pontuacao final, a quantidade de pontos equivalente a 2^ numero de peças restantes
# no tabuleiro e chamar as funcoes que vao fazer com que a movimentacao do robo aconteça dependendo da posicao
#que sera enviada a peça
def primeiraHeuristica():
    global pontuacao
    print("pontuacao: " + str(pontuacao))
    
    #esta lista será a responsável por receber tanto a posicao das quais as peças vao ficar a cada ciclo do while,
    # assim como receberá qual peça deverá ser colocada, ou seja, no auxPositons[0] ficara a posicao no eixo X
    # auxPositions[1], posicao no eixo Y e auxPositions[2] ficará o numero correspondente à peça que sera
    #colocada no lugar referido na propria lista
    auxPositions = []
    #importa booleanos globais
    global circulogrande
    global vezesGrande
    global cruzGrande
    global bolaMedia
    global heuAlternativa
    #so acontece break quando a lista de peças acabar, e ela só acaba quando todas as peças foram colocadas
    while True:
        detect_and_replace_squares2_2(position)
        detect_and_replace_squares_3x3_blocks(position)
        detect_and_replace_squares_4x4_blocks(position)
        detect_and_replace_squares_5x5_sides(position)
        detect_and_replace_lines(position)
        remove_x(position)
        remove_crosses(position)
        if numeros_gerados:
            escolha = numeros_gerados[0]
        i=0
        #caso tenha acabado, retira a pontuacao necessaria e acaba com este while
        if not numeros_gerados:
            removePontuacao=0
            for i in position:
                for j in i:
                    if j!=0 and j!=22:
                        removePontuacao+=1
            pontuacao=pontuacao-(2**removePontuacao)
            print("Acabou")
            print("Esta é a sua pontuacao: " + str(pontuacao))
            return
        #é aqui que ele determina qual metodo desta heuristica vai utilizar
        
        #O valor da lista auxPostions é basicamente um return que o mesmo receberá de outras funcoes
        
        #circulo 5x5
        #apenas acontece se sabe que nao vao haver peças de lixo superiores a um numero do qual resultaria
        # em game over, isso repete-se para a escolha do metodo de formar uma bola 4x4
        if (escolha in(2,3,4,5) and (contar_ocorrencias_numero(2)+contar_ocorrencias_matriz(2))%16<=6 and contar_ocorrencias_numero(2)+contar_ocorrencias_matriz(2)>=16 and containstancias_de_2()<8) or (circulogrande==True and bolaMedia==False and vezesGrande==False and cruzGrande==False and heuAlternativa==False):
            circulogrande=True
            print("Esta é a sua pontuacao: " + str(pontuacao))
            auxPositions = opcaoescolhemaior(escolha)
        #circulo 4x4
        elif (escolha in(2,3,4,5) and (contar_ocorrencias_numero(3)+contar_ocorrencias_numero(5))<11 and contar_ocorrencias_numero(2)%12==0 and contar_ocorrencias_numero(2)>=12) or (circulogrande==False and bolaMedia==True and vezesGrande==False and cruzGrande==False and heuAlternativa==False):
            bolaMedia=True
            print("Esta é a sua pontuacao: " + str(pontuacao))
            auxPositions= opcaoBolaMedia()
        #X maior
        #so vai acontecer, se souber que, além de possuir peças suficientes para fazer um X grande, o numero de
        #peças que serao descartadas é menor que 9, caso contrario isso anularia a quantidade de pontos feitos
        #ao finalizar a figura do X maior
        elif (escolha in(2,3,4,5) and contar_ocorrencias_numero(5)%9==0 and (contar_ocorrencias_numero(3)+contar_ocorrencias_numero(2))<9 and contar_ocorrencias_numero(5)>=9) or (circulogrande==False and bolaMedia==False and vezesGrande==True and cruzGrande==False and heuAlternativa==False):
            print("Esta é a sua pontuacao: " + str(pontuacao))
            vezesGrande=True
            auxPositions=  opcaoescolhemaiorvezes()
        #+ maior
        #segue o mesmo padrao do X maior, apenas muda que ele verifica se possui + suficientes para
        #fazer a figura
        elif (escolha in(2,3,4,5) and contar_ocorrencias_numero(3)>=9 and contar_ocorrencias_numero(3)%9==0  and contar_ocorrencias_numero(4)%2==0 and contar_ocorrencias_numero(2)%4==0 and contar_ocorrencias_numero(5)<9 ) or (circulogrande==False and bolaMedia==False and vezesGrande==False and cruzGrande==True and heuAlternativa==False):
            print("Esta é a sua pontuacao: " + str(pontuacao))
            cruzGrande=True
            auxPositions= opcaocruzGrande()
        
        #caso as peças fornecidas nao sejam viaveis para fazer um dos conjuntos acima, ele faz o metodo geral
        #tambem chamado de heuristicaAlternativa
        else:
            heuAlternativa=True
            auxPositions= heuristicaAlternativa()
        
        #Color running é responsável por chamar a funcao que calculara o melhor caminho ate
        # o local que se quer chegar, partindo de um certo ponto
        colorRunning2(auxPositions[0],auxPositions[1],auxPositions[2])
        
        #verifica se alguma figura foi formada, caso sim, remove essa figura da lista Position e aumenta
        #a pontuacao para a respetiva figura formada
        detect_and_replace_squares2_2(position)
        detect_and_replace_squares_3x3_blocks(position)
        detect_and_replace_squares_4x4_blocks(position)
        detect_and_replace_squares_5x5_sides(position)
        detect_and_replace_lines(position)
        remove_x(position)
        remove_crosses(position)

#esta funcao representa o caso geral da primeira heuristica
def heuristicaAlternativa():
    
    #esta lista receberá as coordenadas x e y onde a peça sera colocada, e o numero da peça na sua posicao
    # de indice 2
    posicoesAColocar = []
    
    #verifica se alguma figura foi formada, antes de qualquer coisa
    detect_and_replace_squares2_2(position)
    detect_and_replace_squares_3x3_blocks(position)
    detect_and_replace_squares_4x4_blocks(position)
    detect_and_replace_squares_5x5_sides(position)
    detect_and_replace_lines(position)
    remove_x(position)
    remove_crosses(position)
    
    #chama as funcoes explicadas anteriormente, estas lidam de uma certa maneira, tendo em conta o tabuleiro
    #ela decidem como vao lidar com uma certa peça recebida
    if numeros_gerados[0] == 2:
        posicoesAColocar=opcao_escolheCirculos()
        posicoesAColocar.append(2)
    elif numeros_gerados[0] == 3:
        posicoesAColocar=opcao_escolhemais()
        posicoesAColocar.append(3)
    elif numeros_gerados[0] == 4:
        posicoesAColocar=opcao_escolheLinhas1()
        posicoesAColocar.append(4)
    elif numeros_gerados[0] == 5:
        posicoesAColocar=opcao_escolhevezes()
        posicoesAColocar.append(5)
    
    #verifica novamente se alguma figura foi formada
    #isto é mais um resíduo de funcoes anteriores, ela nao consegue formar uma figura por si só
    detect_and_replace_squares2_2(position)
    detect_and_replace_squares_3x3_blocks(position)
    detect_and_replace_squares_4x4_blocks(position)
    detect_and_replace_squares_5x5_sides(position)
    detect_and_replace_lines(position)
    remove_x(position)
    remove_crosses(position)
    
        
    print(posicoesAColocar)
    return posicoesAColocar
  
#classe que identifica os nodos utilizados para fazer a nossa heuristica do A* para pathfinding
#este codigo é adaptado para as condicoes que o micropython nos coloca, infelizmente, o micropython nao é
#capaz de suportar certas livrarias que tornariam o pathfinding muito mais simples e até mesmo eficiente
class Node:
    def __init__(self, x, y, obstacle=False):
        self.x = x
        self.y = y
        self.obstacle = obstacle
        self.g = float('inf')
        self.h = float('inf')
        self.f = float('inf')
        self.parent = None

#heuristica do a*
def heuristic(node, goal):
    return abs(node.x - goal.x) + abs(node.y - goal.y)

#Buscas os vizinhos
def get_neighbors(node, grid):
    neighbors = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Adjacent cells

    for dx, dy in directions:
        x, y = node.x + dx, node.y + dy

        if 0 <= x < len(grid) and 0 <= y < len(grid[0]) and not grid[x][y].obstacle:
            neighbors.append(grid[x][y])

    return neighbors

#A*
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

            tentative_g = current.g + 1 #asssume custo de 1

            if tentative_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = tentative_g
                neighbor.h = heuristic(neighbor, goal)
                neighbor.f = neighbor.g + neighbor.h

                if not any(node[2] == neighbor for node in open_set):
                    heapq.heappush(open_set, (neighbor.f, id(neighbor), neighbor))

    return None  # aqui acontece quando nao encontrou caminho


#esta funcao é a funcao utilizada para fazer todo o caminho especifico, ela recebe dois argumentos, estes
#correspondem as posicoes de x e y na nossa grelha, e faz todo o caminho, partindo da posicao [0][0] até uma
#certa posicao [x][y], e depois faz o oposto, da posicao[x][y] até a posicao[0][0]
def setGoalNode(goal_x,goal_y):
    print("x rebecido: ", goal_x)
    print("y rebecido: ", goal_y)
    global tentativas
    global index
    global indexCores
    global north
    global south
    global east
    global west
    rows, cols = len(position), len(position[0])
    grid = [[Node(i, j, position[i][j] !=0 and position[i][j] !=22 and position[i][j] !=44) for j in range(cols)] for i in range(rows)]
    index=0
    #ajusta o movimento do motor de rotacao, basicamente, antes de qualquer
    motorRot.run_target(20,-120)     
    motorRot.run_target(20,0)      
    
    
    start_node = grid[0][0]
    goal_node = grid[goal_x][goal_y]
    print(start_node)
    print(goal_node)
    # faz o a*, retorna todo um caminho, isto é, se queremos por exemplo ir da posicao [0][0] até a [1][2]
    # o path vai conter algo deste tipo [(0,1),(1,1),(1,2)], e é através deste que conseguimos saber o caminho
    # correto e eficiente
    path = a_star(start_node, goal_node, grid) 

    #se nao existir é porque nao é possivel chegar ao local pretendido, seja pelo local estar preso, seja por
    #ja existir uma peça no local
    if path:
        tentativas=0
        #vai fazer todos os caminhos necessarios ate chegar ao ponto final
        for list in path:
            #esta funcao move da posicao inicial ate uma outra posicao
            move_to_position(list[0],list[1])
            utime.sleep(0.2)
            #caso esteja na ultima posicao
            if list[0]==path[-1][0] and list[1]==path[-1][1]:
                #vira o robo dependendo de onde está virado, independentemente, ele precisa estar virado
                #para o norte ao chegar an posicao desejada
                if south==1:
                    turn_to_angle(180)
                if east==1:
                    turn_to_angle(-90)
                if west==1:
                    turn_to_angle(90)
                north=1
                south=0
                east=0
                west=0
            index=index+1
        print("--------------")
        for i in position:
            print(i)
        #move o motor para cima para conseguir deixar a peça na posicao certa, pois ja esta em cima dela
        motorRot.run_target(20,-150)
        
        #faz o caminho inverso para chegar a posicao inicial novamente
        while(index!=0):
            move_to_position(path[index-1][0],path[index-1][1])
            utime.sleep(0.2)
            index=index-1
        #ao chegar a posicao inicial de novo, vira-se para o norte
        if south==1:
            turn_to_angle(180)
        if east==1:
            turn_to_angle(-90)
        if west==1:
            turn_to_angle(90)
        
        north=1
        south=0
        east=0
        west=0
        print("--------------")
        for list2 in position:
            print(list2)
        if numeros_gerados:
            position[goal_x][goal_y] = numeros_gerados[0]
            
        

        print("Este é o indexCores:",indexCores)
        print("--------------")
        for list in position:
            print(list)
        return
    else:
        if tentativas<5:
            print("Nao foi possivel obter um caminho")
            tentativas=tentativas+1
        else:
            print("Provavelmente não será possivel chegar a mais nenhuma posição")
            return
#0 - unnocupied ; 1 - robot position; 2 - blue block; 3 - yellow block; 4 - red block; 5- green block
#nao é mais usado, mas quando era usado, verificava se figuras tinham sido formadas
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
        
#esta funcao é a funcao responsavel por receber as posicoes onde o robo tem de movimentar, verifica
#se a posicao nao esta cheia, evitando assim o programa crashar dentro da funcao setGoalNode
#se a posicao esta vazia, ele vai
#a condicao está para que, se a posicao for diferente de 0, um 22 ou um 44 logo está cheia.
#O 0 significa que está vazio, o 22 e o 44 sao resíduos de outras funcoes que tinhamos antes, outros metodos
#que reservavam posicoes especificas, onde o 22 e o 44 eram apenas projeções de futuras posicoes que ficariam 
#cheias, mas nao necessariamente cheias
#esse método provocou muitas dores de cabeças desnecessárias e era menos eficiente do que o nosso método sequencial
#atual da primeira heuristica
def defineNumerosPosicao(numero1,numero2):

    print(numero1,numero2)
    if(position[numero1][numero2]!=0 and position[numero1][numero2]!=22 and position[numero1][numero2]!=44):
        print("ERRO! - Posicao ocupada, a escolher outra posicao")

        
    else:
        setGoalNode(numero1,numero2)
        position[numero1][numero1]
    

print(initial_state)

#while(1):
    #motorRot.run_target(400,-100)
    #motorRot.run_target(100,-160)
    #motorRot.run_target(100,0)
    #motorRot.track_target(0)

#teste()
#robot.turn(180)

#nao é utilizado, este metodo fazia duas coisas, nas nossas primeira implementacoes, tentamos utilizar o
#giroscopio para tentar fazer o robo virar de maneira mais precisa, mas, acabamos por descobrir que
#o giroscopios é muito dificil de trabalhar, logo paramos de o utilizar
#esta funcao era responsavel por atualizar o valor atual da variavel que guardava o angulo do giroscopio
#e caso o valor excedesse 360, (o que era possivel), ele atualizava o valor para um valor melhor,
#visto que ter +360 graus significa apenas mais uma volta desnecessária que em nada nos ajuda a extrair
#informacao de um angulo, pelo contrário
def get_gyro_angle():
    global gyroSensorAngle
    # Lê a posição atual do sensor giroscópio
    utime.sleep(1)
    gyroSensorAngle = gyro.angle()
    
    printGyroSensorAngle()
    if(gyroSensorAngle!=0):
        if(gyroSensorAngle>360):
            gyroSensorAngle=gyroSensorAngle-360
        robot.turn(-gyroSensorAngle)
    gyroSensorAngle = gyro.angle()
    printGyroSensorAngle()
    # Imprime a posição atual
   
#esta funcao fazia apenas print da variavel que guardava o angulo atual do giroscopio 
def printGyroSensorAngle():
    print(gyroSensorAngle)

#esta funcao é uma das funcoes mais antigas e é utilizada até este momento, ela vira o robô no angulo
#dado como argumento, o target_angle
def turn_to_angle(target_angle, margin_of_error=5, move_speed=50):
    rotate(target_angle)
    utime.sleep(0.2)
    
#esta funcao é utilizada mas de nada influencia o funcionamento do programa tirando talvez o deixar mais lento
#ele basicamente atualizaria a variavel do angulo do sensor buscando retirar os 360 desnecessários e converter
# de angulo negativo para positivo, a variavel gyroSensorAngle é inicializada e nunca sai disso, logo esta funcao
#nunca fara nada de concreto    
def absoluteAngle():                                            #gives the absolute angle which the robot is facing
    global gyroSensorAngle
    if gyroSensorAngle > 360:
        gyroSensorAngle = gyroSensorAngle-360
    if gyroSensorAngle< 0:
        gyroSensorAngle = 360+gyroSensorAngle 

#esta funcao é utilizada para girar o robo em um certo angulo, é a funcao chamada na funcao turn_to_angle
#angle é sempre 0, visto que ele nao esta a ser modificado, basicamente esta funcao foi feita pensando
# em rodar um certo numero de graus, maior ou menor do que o pedido pela chamada da funcao
# para ajustar o robo, ou seja, o angle seria o angulo seria a quantidade de graus que o robo estaria desalinhado
#impreciso
def rotate(after): 
    global angle
    rotation=0
    rotation = after - angle
    absoluteAngle()
    robot.turn(rotation)
    
    
#esta funcao foi uma das primeiras se nao a primeira para efetuar um teste de movimentacao e rotacao do robo
# nao é mais utilizada
def teste():
    robot.straight(300)
    robot.turn(180)
   # arm.on_for_rotations(SpeedPercent(75), 0,1)

#esta funcao nao é utilizada, ela basicamente determinava quanto o robo tinha que se mover em linha reta
def movingPath(moveX, moveY):
    movingX = (moveX - x)* 230
    movingY = (moveY - y)* 230
    if (movingX < 0):
        robot.straight(movingX)
    else:
        robot.straight(movingX)
    robot.straight(movingY)

###############################

#printPosition()

#esta lista supostamente ia guardar a posicao atual do robo, mas nunca chegou a fazer isso
currentPosition = []           #coordinates in the array position above

#esta funcao nao é usada e era usada para retornar o valor da lista anterior
def verifyPosition():
    return currentPosition

#esta é uma funcao que nunca foi terminada
def detectColour():
    return

#esta funcao foi uma tentativa de fazer o robo apanhar um bloco quando tinhamos a ideia do robo
#levantar uma peça e nao de empurra-la
def pickBlock():
    verifyPosition()
    #findPath()
    return

#esta funcao é muito importante, é a funcao responsável por preencher a lista numeros_gerados, com as peças
#correspondentes a uma certa cor e figura, segue a legenda mostrada no inicio do código
#além disso ela também é utilizada para escolher qual heuristica vai ser escolhida, a primeira ou a segunda
#é basicamente responsável pela fase de leitura e escolha de heuristica, dependendo da cor dada, uma
#heuristica sera executada
def detect_and_print_color(color_sensor):
    # Lê a cor atual do sensor de cor
    global pontuacao
    current_color = color_sensor.color()
    

#vai verificar as cores até receber a cor branca
    while(current_color!=Color.WHITE):
        if current_color == Color.GREEN:
            numeros_gerados.append(5)
            ev3.speaker.beep()
            
            utime.sleep(2)
        if current_color == Color.YELLOW:
            numeros_gerados.append(3)
            ev3.speaker.beep()
            utime.sleep(2) 
        if current_color == Color.BLUE:
            numeros_gerados.append(2)
            ev3.speaker.beep()
            utime.sleep(2)
        if current_color == Color.RED:
            numeros_gerados.append(4)
            ev3.speaker.beep()
            utime.sleep(2)
       
        current_color = color_sensor.color()
        print(current_color)
    
    #barulhos para sabermos que terminou a fase de leitura de peças para a lista de peças
    ev3.speaker.beep()
    utime.sleep(0.1)
    ev3.speaker.beep()
    utime.sleep(0.5)
    #ao receber a corr branca alem de sair do while, entra neste if
    if current_color==Color.WHITE:
        ev3.speaker.beep()
        utime.sleep(2)
        
        #só vai sair deste ciclo while se uma das heuristicas for escolhida
        while(True):
            current_color = color_sensor.color()
            print(current_color)
            #se receber amarelo como cor no sensor de cor, executa a segunda heuristica
            if current_color==Color.YELLOW:
                ev3.speaker.beep()
                utime.sleep(0.5)
                ev3.speaker.beep()
                utime.sleep(0.5)
                ev3.speaker.beep()
                utime.sleep(0.5)
                
                #heuristica1
                segundaHeuristica(position, numeros_gerados)
                print("pontuacao: " + str(pontuacao))
                break
            #vermelho ou azul, executa a primeira heuristica
            elif current_color == Color.RED or current_color == Color.BLUE:
                
                #heuristica2
                ev3.speaker.beep()
                utime.sleep(0.1)
                ev3.speaker.beep()
                utime.sleep(0.1)
                
                
                primeiraHeuristica()
                print("pontuacao: " + str(pontuacao))
                break
        # Imprime a cor detectada

#esta funcao foi utilizada para teste e é utilizada aqui também, ela é uma das poucas coisas que nao mudou desde
# o nosso ambiente de simulacao para o ambiente do robo propriamente dito
#serve para mostrar o array de blocos atual e também para mostrar na consola como está a lista que contem as
# posicoes dos blocos
def opcao_2():
    print("1- 2-circulo 3-mais +  4-linhas 5-x")
    mostra_nuemeros_aleatorios()
    print('------------------------------------')
    print('Grelha:')
    for list in position:
        print(list)
    print('------------------------------------')

#faz print da lista de blocos atual
def mostra_nuemeros_aleatorios():
    # Mostra os numeros gerados 
    print('Números gerados aleatoriamente:')
    print(numeros_gerados)

#esta funcao é utilizada para ir para uma certa posicao tendo em conta para onde o robo está virado e vira-lo
#conforme seja necessario o robo pode estar virado para norte, sul, este e oeste
def move_to_position(nextX, nextY):
    #o x e o y sao as posicoes atuais do robo, ou seja, se o robo esta na position[1][2], o x vai ser 1 e o y
    #vai ser 2
    global x
    global y
    global north
    global east
    global south
    global west
    global tamanho_bloco
    
    #caso o valor de x - x que quero ir seja menor que 0, significa que o robo quer se mover para o sul
    if (x - nextX) < 0:
        #estes 3 ifs vao virar o robo no sentido sul, dependendo do sentido atual que o robo esta virado
        if north == 1:
            turn_to_angle(180)
        elif east == 1:
            turn_to_angle(90)
        elif west == 1:   
            turn_to_angle(-90)
        north, south, east, west = 0, 1, 0, 0
        #apos virar, anda, se nao precisar virar, anda na mesma
        robot.straight(tamanho_bloco)
        #atualiza a posicao atual do robo, pois ele moveu-se para baixo pois estava a encarar o sul
        x=x+1

    #aqui é o opost de cima, ele quer mover-se para norte e vai colocar o robo virado para la antes de se mover
    elif (x - nextX) > 0:
        if south == 1:
            turn_to_angle(180)
        elif east == 1:
            turn_to_angle(-90)
        elif west == 1:   
            turn_to_angle(90)
        north, south, east, west = 1, 0, 0, 0
        robot.straight(tamanho_bloco)
        x=x-1
        
    #aqui ele vai verificar se o robo quer ir para a esquerda, pois se o y- y que quero ir for maior que zero,
    # o y que ele quer ir está mais á esquerda, fazendo assim com que ele vire para oeste e e ande um bloco
    elif (y - nextY) > 0:
        if south == 1:
            turn_to_angle(90)
        elif east == 1:
            turn_to_angle(180)
        elif north == 1:   
            turn_to_angle(-90)
        north, south, east, west = 0, 0, 0, 1
      
        robot.straight(tamanho_bloco)
        y=y-1

    #o mesmo do de cima so que para a direção este
    elif (y - nextY) < 0:
        if south == 1:
            turn_to_angle(-90)
        elif west == 1:
            turn_to_angle(180)
        elif north == 1:   
            turn_to_angle(90)
        north, south, east, west = 0, 0, 1, 0
        robot.straight(tamanho_bloco)
        y=y+1

#esta funcao é responsável por chamar a funcao que irá chamar uma outra funcao que fara a movimentacao,
#esta funcao era utilizada antes para fazer a verificação de figuras, mas com a mudança na estrutura
# e no funcionamento do codigo e consequentemente do robo, a verificacao de figuras passou a ser algo
# mais frequente e internos nas funcoes que alteram as posicoes das peças na grelha
#tambem imprime a pontuacao
def colorRunning(numero1,numero2):

    #checkPositions()
    defineNumerosPosicao(numero1,numero2)
    ev3.speaker.beep()
    utime.sleep(0.5)
    #checkPositions()
    print("----------------")
    for i in position:
        print(i)
    print("----------------")
    print("Pontuação: ",pontuacao)

#esta funcao é uma copia da funcao acima, mas com nome diferente
# é usada em outra heuristica, basicamente ela teria diferenças, mas
# no final ela acabou por ficar igual
def colorRunning2(numero1,numero2,posicao):

    #checkPositions()
    defineNumerosPosicao(numero1,numero2)
    ev3.speaker.beep()
    utime.sleep(0.5)
    #checkPositions()
    position[numero1][numero2]=posicao
    print("----------------")
    for i in position:
        print(i)
    print("----------------")
    print("Pontuação: ",pontuacao)
        
        
        
        
# move_to_position(0,1)
# move_to_position(0,2)
# move_to_position(0,3)
# move_to_position(0,2)
# move_to_position(1,2)
# move_to_position(1,3)

#agarraBloco()



# index=0
# motorRot.run_target(20,80)
# if path:
#     for list in path:
#         move_to_position(list[0],list[1])
#         index=index+1
#     robot.straight(50)
#     motorRot.run_target(20,0)
#     robot.straight(-50)
    
#     while(index!=0):
#         move_to_position(path[index-1][0],path[index-1][1])
#         index=index-1
    
    
# else:
#     print("Nao conseguiu encontrar um caminho")

#Aqui é a execução do  codigo, é através da detect_and_print_color que todo o processo que envolve o funciona
#mento do robo começa e também termina
detect_and_print_color(line_sensor)

#isto é para garantir que o robo termina de fazer tudo e a gaiola que a peça fica dentro, fica no chao
# é usado para caso queiramos correr varias vezes o robo, assim ele nao perde a referencia do ponto inicial da posicao
# da gaiola
motorRot.run_target(20,0) 

#mostra que acabou e mostra a pontuacao final, esta é a pontuacao mais fidedigna pois é a pontuacao pós todos
# os métodos aplicados a mesma, existem pontuacoes que aparecem antes desta mas nao representam a real pontuacao
# pois sao chamada antes dos metodos de atualizacao de pontuacao
print("Acabou")
print("Esta é a sua pontuacao FINAL!!!: " + str(pontuacao))

