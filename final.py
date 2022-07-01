from mimetypes import guess_all_extensions
from operator import index, le
from pdb import runcall
import cv2
import RobotAPI as rapi
import RPi.GPIO as IO
import numpy as np
import serial
import time

port = serial.Serial("/dev/ttyS0", baudrate=115200, stopbits=serial.STOPBITS_ONE) # Подключаем UART на Raspberry PI
robot = rapi.RobotAPI(flag_serial=False) # Создаем робота, чтобы мы могли использовать функции связанные с передачем изображения
robot.set_camera(100, 640, 480) # Задаем разрешение камеры и максимальный FPS

IO.setwarnings(False)
IO.setmode (IO.BCM)
IO.setup(18,IO.IN) 

message = '999999999$'
ii = ''
fps = 0
fps1 = 0
fps_time = 0

xright21, yright21 = 390, 230
xright22, yright22 = 640, 270

xleft11, yleft11 = 0, 230
xleft12, yleft12 = 250, 270

xright41, yright41 = 590, 205
xright42, yright42 = 640, 230

xleft31, yleft31 = 0, 205
xleft32, yleft32 = 50, 230

xBl1, yBl1 = 320, 345
xBl2, yBl2 = 350, 365

xOl1, yOl1 = 290, 345
xOl2, yOl2 = 320, 365

xObj1, yObj1 = 110, 140
xObj2, yObj2 = 530, 330
# Инициализация констант для координат областей интереса

count = 0
x1 = 1130
x, y = 300, 200
w, h = 40, 80
a = ''
t_cube = 0.2
sp = 0
per = 0
temp = 0
t_y = 0
# Инициализация доп. отладочных переменных

speed = 50
max_speed = 50
min_speed = 50
# Инициализация констант для скорости движения робота

Right_color = 0
Left_color = 0
# Инициализация констант для светодиодов

kp = 0.2
kd = 0.2
kp1 = 0.3
kd1 = 0.3
kp2 = kp1 / 3
kd2 = kd1 / 3
e = 0
e_old = 0
sr1 = 0
sr2 = 0
Objsr = 0
# Инициализация констант для PD регулятора

gsr = 0
rsr = 0
yred = 0
yred_old = 0
ygr = 0
ygr_old = 0
# Инициализация констант с положение кубиков

Object_green = 0
Object_red = 0
# Инициализация констант с кол-во кубиков

index_section = 0
index_section = 0
index_time = 0
# Инициализация констант-индексов для массивов

rul = 0
deg = 0
deg1 = 0
# Инициализация констант для управления серводвигателем

left_sensor = 0
right_sensor = 0
# Инициализация констант для датчиков стенок

tper = time.time()
t_obj =time.time()
t_red = time.time()
t_green = time.time()
time_index = time.time()
time_section = time.time()
time_button = time.time()
# Инициализация таймеров

lowBl = np.array([97, 90, 20]) # Синяя линия
upBl = np.array([110, 255, 125])

lowOl = np.array([5, 60, 60]) # Оранжевая линия
upOl = np.array([24, 180, 179])

lowObjgreen = np.array([57, 145, 53]) # Зеленый кубик
upObjgreen = np.array([83, 255, 255])

lowObjyellow = np.array([27, 167, 99]) # Желтый кубик
upObjyellow = np.array([42, 255, 231])

lowObjred = np.array([0, 135, 50]) # Красный кубик
upObjred = np.array([8, 255, 255]) 
 
lowObjred1 = np.array([165, 135, 50]) # Красный кубик
upObjred1 = np.array([180, 255, 255]) 
# Инициализация констант для hsv

section = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
time_line_to_line = [0, 0, 0, 0]
time_line_to_obj = [[0, 0], [0, 0], [0, 0], [0, 0]]
# Инициализация массивов для записи кубиков и времени

keyboardcontrol = 'None'
direction = 'None'
state = '0'
# Инициализация переменных с состояниями

Flag_line_blue = False
Flag_line_orange = False
Flag_button = False
Flag_obj_green = False
Flag_obj_red = False
Flag_line = False
Flag_index_red = False
Flag_index_green = False
Flag_time_section = False
Flag_turn_green = False
Flag_turn_red = False
Flag_test_red = True
Flag_test_green = True
# Инициализация Флагов

def black_line(): # Функция для определения черных стен
    global xright21, yright21, xright22, yright22, left_sensor, right_sensor
    datb1 = frame[yleft11:yleft12, xleft11:xleft12] # Забираем из изображения с камеры область интереса
    dat1 = cv2.GaussianBlur(datb1, (9, 9), cv2.BORDER_DEFAULT) # Делаем размытие по гауссу для лучшего распознования
    gray1 = cv2.cvtColor(dat1, cv2.COLOR_BGR2GRAY) # Переводим изображение из RGB в серую
    _, maskd1 = cv2.threshold(gray1, 40, 255, cv2.THRESH_BINARY_INV) # С помощью Threshold мы находим маску чёрного на изображении 
    gray11 = cv2.cvtColor(maskd1, cv2.COLOR_GRAY2BGR) # Переводим серое изображение в RGB  
    frame[yleft11:yleft12, xleft11:xleft12] = gray11 # Отрисовываем датчик на экран
    imd1, contoursd1, hod1 = cv2.findContours(maskd1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # Находим контуры по маске maskd1
    sr1 = 0
    max1 = 0
    for contorb1 in contoursd1:
        x1, y1, w1, h1 = cv2.boundingRect(contorb1) # Координаты, высота и ширина найденного контура
        a1 = cv2.contourArea(contorb1) # Площадь найденного контура
        if a1 > 200 and a1 / (h1 * w1) > 0.3 and a1 > max1: # Фультр, отсекает шумы по пллощади, заполнению контура и находит наибольший контур
            sr1 = h1 * (x1 + w1) # Записыва площадь контура внутри датчика
            max1 = a1 # Перезаписываем максимальную площадь
            cv2.rectangle(datb1, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2) # Обводим контур
    

    datb2 = frame[yright21:yright22, xright21:xright22] # Забираем из изображения с камеры область интереса
    dat2 = cv2.GaussianBlur(datb2, (9, 9), cv2.BORDER_DEFAULT) # Делаем размытие по гауссу для лучшего распознования
    gray2 = cv2.cvtColor(dat2, cv2.COLOR_BGR2GRAY) # Переводим изображение из RGB в серую
    _, maskd2 = cv2.threshold(gray2, 40, 255, cv2.THRESH_BINARY_INV) # С помощью Threshold мы находим маску чёрного на изображении 
    gray12 = cv2.cvtColor(maskd2, cv2.COLOR_GRAY2BGR) # Переводим серое изображение в RGB
    frame[yright21:yright22, xright21:xright22] = gray12 # Отрисовываем датчик на экран
    imd1, contoursd2, hod1 = cv2.findContours(maskd2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # Находим контуры по маске maskd2
    sr2 = 0
    max2 = 0
    for contorb2 in contoursd2:
        x1, y1, w1, h1 = cv2.boundingRect(contorb2) # Координаты, высота и ширина найденного контура
        a1 = cv2.contourArea(contorb2) # Площадь найденного контура
        if a1 > 200 and a1 / (h1 * w1) > 0.3 and a1 > max2: # Фультр, отсекает шумы по пллощади, заполнению контура и находит наибольший контур
            sr2 = h1 * (250 - x1) # Записыва площадь контура внутри датчика
            max2 = a1 # Перезаписываем максимальную площадь
            cv2.rectangle(datb2, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2) # Обводим контур

    datb3 = frame[yleft31:yleft32, xleft31:xleft32] # Забираем из изображения с камеры область интереса
    dat3 = cv2.GaussianBlur(datb3, (9, 9), cv2.BORDER_DEFAULT) # Делаем размытие по гауссу для лучшего распознования
    gray3 = cv2.cvtColor(dat3, cv2.COLOR_BGR2GRAY) # Переводим изображение из RGB в серую
    _, maskd3 = cv2.threshold(gray3, 40, 255, cv2.THRESH_BINARY_INV) # С помощью Threshold мы находим маску чёрного на изображении 
    gray13 = cv2.cvtColor(maskd3, cv2.COLOR_GRAY2BGR) # Переводим серое изображение в RGB
    frame[yleft31:yleft32, xleft31:xleft32] = gray13 # Отрисовываем датчик на экран
    imd1, contoursd3, hod1 = cv2.findContours(maskd3, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # Находим контуры по маске maskd3
    sr3 = 0
    max3 = 0
    for contorb3 in contoursd3:
        x1, y1, w1, h1 = cv2.boundingRect(contorb3) # Координаты, высота и ширина найденного контура
        a1 = cv2.contourArea(contorb3)  # Площадь найденного контура
        if a1 > 200 and a1 / (h1 * w1) > 0.3 and a1 > max3:  # Фультр, отсекает шумы по пллощади, заполнению контура и находит наибольший контур
            sr3 = h1 * (x1 + w1) # Записыва площадь контура внутри датчика
            max3 = a1 # Перезаписываем максимальную площадь
            cv2.rectangle(datb3, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2) # Обводим контур
    

    datb4 = frame[yright41:yright42, xright41:xright42] # Забираем из изображения с камеры область интереса
    dat4 = cv2.GaussianBlur(datb4, (9, 9), cv2.BORDER_DEFAULT) # Делаем размытие по гауссу для лучшего распознования
    gray4 = cv2.cvtColor(dat4, cv2.COLOR_BGR2GRAY) # Переводим изображение из RGB в серую
    _, maskd4 = cv2.threshold(gray4, 40, 255, cv2.THRESH_BINARY_INV) # С помощью Threshold мы находим маску чёрного на изображении 
    gray14 = cv2.cvtColor(maskd4, cv2.COLOR_GRAY2BGR) # Переводим серое изображение в RGB
    frame[yright41:yright42, xright41:xright42] = gray14 # Отрисовываем датчик на экран
    imd1, contoursd4, hod1 = cv2.findContours(maskd4, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # Находим контуры по маске maskd4
    sr4 = 0
    max4 = 0
    for contorb4 in contoursd4:
        x1, y1, w1, h1 = cv2.boundingRect(contorb4) # Координаты, высота и ширина найденного контура
        a1 = cv2.contourArea(contorb4) # Площадь найденного контура
        if a1 > 200 and a1 / (h1 * w1) > 0.3 and a1 > max4: # Фультр, отсекает шумы по пллощади, заполнению контура и находит наибольший контур
            sr4 = h1 * (50 - x1) # Записыва площадь контура внутри датчика
            max4 = a1 # Перезаписываем максимальную площадь
            cv2.rectangle(datb4, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2) # Обводим контур


    left_sensor = int((sr1 + sr3) / 100) # Вычисляем значение для левого датчика линни
    right_sensor = int((sr2 + sr4) / 100) # Вычисляем значение для правого датчика линии
    
    

def blue_line(): # Функция для определения синей линии 
    global max2, yBl1, yBl2, xBl1, xBl2, t, per, sr, state, direction, Flag_line_blue, Flag_line, index_section, time_index, Right_color, Left_color, Flag_time_section, index_time, time_section
    line = frame[yBl1:yBl2, xBl1:xBl2] # Забираем из изображения с камеры область интереса
    cv2.rectangle(frame, (xBl1, yBl1), (xBl2, yBl2), (0, 0, 255), 2) # Обводим датчик синей линии
    hsv = cv2.cvtColor(line, cv2.COLOR_BGR2HSV) # Переводим изображение из RGB в HSV
    mask = cv2.inRange(hsv, lowBl, upBl) # С помощью inRange мы находим маску синего на изображении
    gray1 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) # Переводим изображение из серого в RGB
    frame[yBl1:yBl2, xBl1:xBl2] = gray1 # Отрисовываем датчик на экран
    imd, contours, h = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # Находим контуры по маске mask
    max2 = 0
    for contor in contours:
        x1, y1, w1, h1 = cv2.boundingRect(contor) # Координаты, высота и ширина найденного контура
        a1 = cv2.contourArea(contor) # Площадь найденного контура
        if a1 > 100: # Убираем шумы по площади
            cv2.rectangle(line, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2) # Обводим контур

            Flag_line_blue = True
            Flag_line = True
            # Поднятие флагов при определении линии
            direction = 'Blue'
            # Изменение переменной направления
            Right_color = 3
            Left_color = 3
            # Включение светодиодов для индикации
            index_time = 0
            index_section = 0
            # Изменение индекса для массивов



def orange_line(): # Функция определения оранжевой линии
    global max2, yOl1, yOl2, xOl1, xOl2, t, per, sr, state, direction, Flag_line_orange, Flag_line, index_section, time_index, Right_color, Left_color, index_time, time_section, Flag_time_section
    line = frame[yOl1:yOl2, xOl1:xOl2] # Забираем из изображения с камеры область интереса
    cv2.rectangle(frame, (xOl1, yOl1), (xOl2, yOl2), (0, 0, 255), 2) # Обводим датчик оранжевой линии
    hsv = cv2.cvtColor(line, cv2.COLOR_BGR2HSV) # Переводим изображение из RGB в HSV
    mask = cv2.inRange(hsv, lowOl, upOl) # С помощью inRange мы находим маску оранжевого на изображении
    rmask = cv2.inRange(hsv.copy(), lowObjred, upObjred) # С помощью inRange мы находим маску красного на изображении
    rmask2 = cv2.inRange(hsv.copy(), lowObjred1, upObjred1) # С помощью inRange мы находим маску красного на изображении
    rmask3 = cv2.bitwise_or(rmask, rmask2) # С помошью bitwise_or складываем две максик красного
    mask2 = cv2.bitwise_and(mask, cv2.bitwise_not(rmask3)) # С помошью bit_wise_and и bitwise_not убираем красный, который будет мешать при определении 
    gray1 = cv2.cvtColor(mask2, cv2.COLOR_GRAY2BGR) # Переводим изображение из серого в RGB
    frame[yOl1:yOl2, xOl1:xOl2] = gray1 # Отрисовываем датчик на экран
    imd, contours, h = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # Находим контуры по маске mask2
    max2 = 0
    for contor in contours:
        x1, y1, w1, h1 = cv2.boundingRect(contor) # Координаты, высота и ширина найденного контура
        a1 = cv2.contourArea(contor) # Площадь найденного контура
        if a1 > 50: # Убираем шумы по площади
            cv2.rectangle(line, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2) # Обводим контур

            Flag_line_orange = True
            Flag_line = True
            # Поднятие флагов при определении линии
            direction = "Orange"
            # Изменение переменной направления
            Right_color = 4
            Left_color = 4
            # Включение светодиодов для индикации
            index_time = 0
            index_section = 0
            # Изменение индекса для массивов


def object_(): # Фукция для распознования кубиков
    global Flag_index_green, section, rsr, gsr, xObj1, xObj2, yObj1, yObj2, Flag_obj_green, Flag_obj_red, state, ygr, yred, t_green, t_red, t_cube, Object_red, Object_green, t_y, per, index_section, Flag_index_red, Right_color, Left_color, index_time, time_section, Flag_turn_red, Flag_turn_green, yred_old, ygr_old, Flag_test_red, Flag_test_green
    cube = frame[yObj1:yObj2, xObj1:xObj2] # Забираем из изображения с камеры область интереса
    Gauss = cv2.GaussianBlur(cube, (3, 3), cv2.BORDER_DEFAULT) # Делаем размытие по гауссу для лучшего распознования
    hsv = cv2.cvtColor(Gauss, cv2.COLOR_BGR2HSV) # Переводим изображение из RGB в HSV
    rmask = cv2.inRange(hsv.copy(), lowObjred, upObjred) # С помощью inRange мы находим маску красного на изображении
    rmask2 = cv2.inRange(hsv.copy(), lowObjred1, upObjred1) # С помощью inRange мы находим маску красного на изображении
    rmask3 = cv2.bitwise_or(rmask, rmask2) # Складываем две маски карсного так как крансый может находится с двух сторон диапазона hsv
    max1 = 0
    # hsv1 = cv2.cvtColor(rmask3.copy(), cv2.COLOR_GRAY2BGR)  
    # frame[yObj1:yObj2, xObj1:xObj2] = hsv1
    cv2.rectangle(frame, (xObj1, yObj1), (xObj2, yObj2), (255, 0, 0), 2) # Обводим датчик для кубиков
    _, rcnt, h = cv2.findContours(rmask3, cv2.RETR_EXTERNAL, cv2.BORDER_DEFAULT) # Находим контуры по маске rmask3
    if len(rcnt) != 0: # Проверка массива на наличие объектов     
        for i in rcnt:
            x1, y1, w1, h1 = cv2.boundingRect(i) # Площадь найденного контура
            a1 = cv2.contourArea(i) # Убираем шумы по площади
            if a1 > max1: # Находим самый большой контур
                if a1 > 200 and a1 / (h1 * w1) > 0.5 and w1 < 270: # Фультр, отсекает шумы по пллощади, заполнению контура и длине
                    # if 50 < x1 < 530 and y1 > 50 or 50 < x1 < 530 and y1 < 290:
                        rsr = x1 + w1 # Находим правый угол красного кубика
                        Flag_obj_red = True # Поднимаем флаг, который показывает, что кубики перед нами
                        max1 = a1 # Перезаписываем максимальную площадь
                        yred = y1+h1 # Находим координату нижней грани кубика, для лучшей работы алгоритма
                        if yred > 70: # Если кубика стал нижу четвётрой части датчика, то поднимаем флаг поворота для красного
                            Flag_turn_red = True
                        
                        Right_color = 1
                        Left_color = 1
                        # Влючаем светодиоды красным цветом

                        Flag_turn_green = False # Опускаем флаг поворта для зеленого

                        t_red = time.time() 
                        t_y = time.time()
                        # Записываем время, когда нашли кубик(общее и для красного кубика)
                        if yred > 150 and Flag_test_red: # Если кубик стал ниже половины датчика и Flag_test_red = True, то записываем в массив цвет кубика, время от кубика до линии и меняем индексы
                            section[per % 4][index_section] = 5
                            time_line_to_obj[per % 4][index_section] = round(time.time() - time_section, 2)
                            index_section = 1
                            index_time = 1
                            Object_red += 1
                            Flag_test_red = False
                            Flag_index_red = False
                        if Flag_test_red == False and yred < 150: # Если кубик стал выше половины и Flag_test_red = False, то поднимаем флаги для записи в массивы
                            Flag_test_red = True
                            Flag_index_red = True
                        yred_old = yred
                        # state = "Object"
                        # cv2.circle(cube, ((x1 + y1) // 2), 5, (0, 0, 255), 2)
                        
                        cv2.rectangle(cube, (x1, y1), (x1 + w1, y1 + h1), (0, 0, 255), 2) # Обводим кубик
                else:
                     if t_red + 0.05 < time.time(): # Если время прошло, то опускаем флаг для красного кубика поднимаем флаг для записи в массивы
                        rsr = 0
                        Flag_test_red = True
                        yred = 0
                        Flag_obj_red = False
                        
    else: # Если массив пустой, то через вермя мы пишем, что он пропал
        
        if t_red + 0.05 < time.time(): # Если время прошло, то опускаем флаг для красного кубика поднимаем флаг для записи в массивы
            Flag_test_red = True
            rsr = 0
            yred = 0
            Flag_obj_red = False
              
                
                

    # gmask = cv2.inRange(cv2.cvtColor(cv2.GaussianBlur(frame[yObj1:yObj2, xObj1:xObj2]), 1), lowObjgreen, upObjred)
    gmask = cv2.inRange(hsv.copy(), lowObjgreen, upObjgreen) # С помощью inRange мы находим маску зеленого на изображении
    _, gcnt, h = cv2.findContours(gmask, cv2.RETR_EXTERNAL, cv2.BORDER_DEFAULT) # Находим контуры по маске gmask
    max1 = 0
    if len(gcnt) != 0: # Проверка массива на наличие объектов  
        for i in gcnt:
            x1, y1, w1, h1 = cv2.boundingRect(i) # Площадь найденного контура
            a1 = cv2.contourArea(i) # Убираем шумы по площади
            if a1 > max1: # Находим самый большой контур
                if a1 > 250 and a1 // (h1 * w1) < 0.6: # Фультр, отсекает шумы по пллощади, заполнению контура и длине
                    # if 50 < x1 < 470 and y1 > 70 or 50 < x1 < 470 and y1 < 130:
                        max1 = a1 # Перезаписываем максимальную площадь
                        gsr = x1 # Находим левый угол зеленого кубика
                        ygr = y1+h1 # Находим координату нижней грани кубика, для лучшей работы алгоритма
                        Flag_obj_green = True # Поднимаем флаг, который показывает, что кубики перед нами
                        if ygr > 70: # Если кубика стал нижу четвётрой части датчика, то поднимаем флаг поворота для зеленого 
                            Flag_turn_green = True

                        Right_color = 2
                        Left_color = 2
                        # Влючаем светодиоды зеленым цветом 

                        Flag_turn_red = False # Опускаем флаг поворта для красного

                        t_green = time.time()
                        t_y = time.time()
                        # Записываем время, когда нашли кубик(общее и для зеленого кубика)
                        if ygr > 150 and Flag_test_green: # Если кубик стал ниже половины датчика и Flag_test_green = True, то записываем в массив цвет кубика, время от кубика до линии и меняем индексы
                            section[per % 4][index_section] = 3
                            time_line_to_obj[per % 4][index_time] = round(time.time() - time_section, 2)
                            index_time = 1
                            index_section = 1
                            Object_green += 1
                            Flag_test_green = False
                            Flag_index_green = False
                        if Flag_test_green == False and ygr < 150: # Если кубик стал выше половины и Flag_test_green = False, то поднимаем флаги для записи в массивы
                            Flag_test_green = True
                            Flag_index_green = True
                        ygr_old = ygr
                        # state = "Object"
                        # cv2.circle(cube, ((x1 + y1) // 2), 5, (0, 255, 0), 2)
                        Flag_test = False
                        cv2.rectangle(cube, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2)
                else:
                     if t_green + 0.05 < time.time(): # Если время прошло, то опускаем флаг для красного кубика поднимаем флаг для записи в массивы
                        gsr = 0
                        Flag_test_green = True 
                        ygr = 0
                        Flag_obj_green = False         
                    
    else: # Если массив пустой, то через вермя мы пишем, что он пропал
             
        if t_green + 0.05 < time.time(): # Если время прошло, то опускаем флаг для красного кубика поднимаем флаг для записи в массивы
            gsr = 0 
            Flag_test_green = True
            ygr = 0
            Flag_obj_green = False
                  
            
    
    if Flag_obj_green ==  True and  Flag_obj_red == True: # Если мы видим два кубика разных цветов, то мы будем ехать по кубику, который находится ближе (опкускаем флаг)
        if ygr > yred:
            Flag_obj_red = False
        else:
            Flag_obj_green = False  
   
 
def index(): # Эта функция с помощью времени расставляет кубики на правильные позиции
    global index_section, time_section, index_time
    for ind in range(4): # Цикл перебирает массив с цветами кубиков

        if section[ind][0] != 0 and section[ind][1] != 0: # Если в одной зоне два кубика, то мы ставим их в две крайние позиции
            section[ind][2] = section[ind][1]
            section[ind][1] = 0

        elif section[ind][0] != 0 and section[ind][1] == 0: # Если в первой ячейке массива есть кубик и во второй ячейке массива нет кубака, то мы делим время от линии до кубика на время от линии до линии и получаем процент. 
            if time_line_to_line[ind] != 0:
                if time_line_to_obj[ind][0] / time_line_to_line[ind] > 0.65: 
                    section[ind][2] = section[ind][0]
                    section[ind][0] = 0
                elif time_line_to_obj[ind][0] / time_line_to_line[ind] < 0.64 and time_line_to_obj[ind][0] / time_line_to_line[ind] > 0.4:
                    section[ind][1] = section[ind][0]
                    section[ind][0] = 0

            

while True: # Основной цикл программы 
    Button = (IO.input(18)) # считывание кнопки для запуска программы
    key = robot.get_key() # Считываение кнопок с клавиатуры для ручного управление
    if key == 13: # Переход в ручное управление
        state = "1"
    if key == 27: # Переход в основное состояние, в котором робот обруливает кубики
        state = "Move"
        speed = 50
        max_speed = 50
        min_speed = 50
    if key == 32: # Вывод данных массивов
        index()
        print("  ")
        print(section)  
        time.sleep(1)
        print(time_line_to_line)
        time.sleep(1)
        print(time_line_to_obj)

    # if key != -1:
    #     print(key)

    frame = robot.get_frame(wait_new_frame=1) #Получаем кадр с камеры на роботе

    fps1 += 1 # Счётчик кадров в секунду
    if time.time() > fps_time + 1:
        fps_time = time.time()
        fps = fps1
        fps1 = 0

    if state == '0': # Состояние "0" - это ожидание загрузки робота и нажатия на кнопку
        if Flag_button == False:
            message = '999999999$'
        else:
            message = str(speed + 200) + str(deg + 2000) + str(Right_color) + str(Left_color) + '$' # Формирует сообщение на Pyboard (Скорость мотора, угол поворота серводвигателя, цвет светодиодов)
        if Button == False and time_button + 1 < time.time():
            state = 'Move' # Переход в состояние основной программы
            direction = 'None' # Направление движения робота (Orange или Blue) в данном случае None, так как робот еще не начал движение
            Flag_button = True
            Right_color = 2
            Left_color = 2
            # Цвета светодиодов
            speed = 50
            max_speed = 50
            min_speed = 50
            # Скорость мотора
            time_button = time.time() 
            # Таймер кнопик
        if Button:
            pass

    if state != '0' and state != 'Stop': # Состояние ручного управления
        if state == '1':
            Right_color = 2
            Left_color = 2
            sp += 1
            if key != -1:
                if key == 87:
                    speed = 35
                    sp = 0
                if key == 83:
                    speed = -35
                    sp = 0
                if key == 65:
                    deg1 = 35
                    sp = 0
                if key == 68:
                    deg1 = -35
                    sp = 0
            if sp > 10:
                speed = 0
                deg1 = 0
                sp = 11
            




        if state == "Move": # Основное состояние программы, в ней робот едет по кругу и обруливает кубики
            Objsr = 0
            Flag_line = False
            Flag_line_blue = False
            Flag_line_orange = False
            # Каждую итерацию Цикла все основные перменные

            if direction == "Blue": # В зависимости от направление выключается один из датчиков линии
                blue_line()

            elif direction == "Orange":
                orange_line()
            else: # Иначе работают оба  
                blue_line()
                orange_line()

            object_() # Функция для определения кубиков
            black_line() # Функция для езды по стенам

            e = left_sensor - right_sensor # Вычисление ошибки
            if -5 < e < 5: # Фильтр на маленькие шумы
                e = 0
            u = e * kp + (e - e_old)*kd # pd регулятор

            if Flag_obj_red: # Если есть красный кубик, то один из датчик мы убираем один из датчиков в зависимости от направления
                if direction == "Orange":
                    right_sensor = 0
                else:
                    left_sensor = 0
                Objsr  = round(230 - yred * 0.85) # Функция, которая высчитывает среднее значение, по которому робот будет ехать(Оно нестатичное, так как в зависимости от растояния значения будут разные)
                if Objsr < 50: # Ограничение среднего значения 
                    Objsr = 50
                e = rsr - Objsr # Вычисление ошибки
                if -5 < e < 5: # Фильтр на маленькие шумы
                    e = 0

                if yred < 70: # Если кубик находится далеко, то мы уменьшаем кооэффиценты в два раза
                    kp_cube = kp2
                    kd_cube = kd2
                else: # Иначе делаем их 0.3
                    kp_cube = kp1
                    kd_cube = kd1

                u = e * kp_cube + (e - e_old) * kd_cube # pd регулятор
                robot.text_to_frame(frame, "Red", 100, 100) # Пишем на экран текущий кубик

            if Flag_obj_green: # Если есть зеленый кубик, то один из датчик мы убираем один из датчиков в зависимости от направления
                if direction == "Orange":
                    right_sensor = 0
                else:
                    left_sensor = 0
                Objsr  = round(190 + ygr * 0.85) # Функция, которая высчитывает среднее значение, по которому робот будет ехать(Оно нестатичное, так как в зависимости от растояния значения будут разные)
                if Objsr > 490: # Ограничение среднего значения 
                    Objsr = 490
                e = gsr - Objsr # Вычисление ошибки
                if -5 < e < 5: # Фильтр на маленькие шумы
                    e = 0

                if ygr < 70: # Если кубик находится далеко, то мы уменьшаем кооэффиценты в два раза
                    kp_cube = kp2
                    kd_cube = kd2
                else: # Иначе делаем их 0.3
                    kp_cube = kp1
                    kd_cube = kd1
                
                u = e * kp_cube + (e - e_old)*kd_cube # pd регулятор
                robot.text_to_frame(frame, "Green", 100, 100) # Пишем на экран текущий кубик

            deg = int(rul - u) # Записываем в переменную deg нужный угол поворота серводвигаетлся
            if deg < -50: # Ограничение угла поворота серводвигателя
                deg = -50
                
            if deg > 50: # Ограничение угла поворота серводвигателя
                deg = 50

            e_old = e # Перезаписываем старую ошибку

            if Flag_obj_green == False and Flag_obj_red == False: # Поворот если пропали кубики и стены
                if t_y + 0.4 > time.time(): # Если время не вышло, то мы опускаем датчики
                    if direction == 'Orange' and Flag_turn_green:
                        right_sensor = 0
                    elif direction == 'Blue' and Flag_turn_red:
                        left_sensor = 0
                else:
                    Flag_turn_red = False
                    Flag_turn_green = False



                Right_color = 0
                Left_color = 0 
                if right_sensor <= 10: # Если на правом датчки ничего нет, то мы поворачиваем направо
                    deg = -50
                    speed = min_speed

                if left_sensor <= 10: # Если на левом датчки ничего нет, то мы поворачиваем налево
                    deg = 50
                    speed = min_speed

                if left_sensor <= 10 and right_sensor <= 10: # Если два датчика пропали, то поворачиваем в зависимости от направления
                    speed = min_speed
                    if direction == 'None':
                        deg = 0
                    elif direction == 'Orange':
                        deg = -50
                    else:
                        deg = 50
                
            
            if Flag_line and tper + 0.5 < time.time(): # Подсчёт перекрестков и запись времени в массив
                    time_line_to_line[per % 4] = round(time.time() - time_section, 2) 
                    per += 1
                    tper = time.time()
                    time_section = time.time()


            if per // 4 == 3: # Условие перехода в состояние финиша 
                state = "Finish"
                t_finish = time.time()
            

        if state == "Finish": # Состояние финиша, в котором робот едет половину времени от стартовой зоны 
            if t_finish + time_line_to_line[0] / 2 > time.time():
                Objsr = 0
                object_() # Функция для определения кубиков
                black_line() # Функция для езды по стенам

                e = left_sensor - right_sensor # Вычисление ошибки
                if -5 < e < 5: # Фильтр на маленькие шумы
                    e = 0
                u = e * kp + (e - e_old)*kd # pd регулятор

                if Flag_obj_red: # Если есть красный кубик
                    Objsr  = round(230 - yred * 0.9) # Функция, которая высчитывает среднее значение, по которому робот будет ехать(Оно нестатичное, так как в зависимости от растояния значения будут разные)
                    e = rsr - Objsr # Вычисление ошибки
                    if -5 < e < 5: # Фильтр на маленькие шумы
                        e = 0
                    u = e * kp1 + (e - e_old)*kd1 # pd регулятор
                    robot.text_to_frame(frame, "Red", 100, 100) # Пишем на экран текущий кубик

                if Flag_obj_green: # Если есть зеленый кубик
                    Objsr  = round(190 + ygr * 0.9) # Функция, которая высчитывает среднее значение, по которому робот будет ехать(Оно нестатичное, так как в зависимости от растояния значения будут разные)
                    e = gsr - Objsr # Вычисление ошибки  
                    if -5 < e < 5: # Фильтр на маленькие шумы
                        e = 0
                    u = e * kp1 + (e - e_old)*kd1 # pd регулятор
                    robot.text_to_frame(frame, "Green", 100, 100) # Пишем на экран текущий кубик

                deg = int(rul - u) # Записываем в переменную deg нужный угол поворота серводвигаетлся
                if deg < -50:  # Ограничение угла поворота серводвигателя
                    deg = -50
                    
                if deg > 50:  # Ограничение угла поворота серводвигателя
                    deg = 50

                e_old = e # Перезаписываем старую ошибку

                if Flag_obj_green == False and Flag_obj_red == False: # Поворот если пропали кубики и стены
                    if right_sensor == 0: # Если на правом датчки ничего нет, то мы поворачиваем направо
                        deg = -50

                    if left_sensor == 0:  # Если на левом датчки ничего нет, то мы поворачиваем налево
                        deg = 50

                    if right_sensor == 0 and left_sensor == 0: # Если два датчика пропали, то поворачиваем в зависимости от направления
                        if direction == 'None':
                            deg = 0
                        elif direction == 'Orange':
                            deg = -50
                        else:
                            deg = 50
                    
                
            else: # Когда время выйдет робот остановится и поставит колеса в нулевое положение
                speed = 0
                max_speed = 0
                min_speed = 0
                deg = rul            

        if state == "1": # Нужно для ручного управление, так как переменная deg может конфликтовать
            deg = deg1 
        deg = -(deg + 13) # Инвертирование руля 
        message = str(speed + 200) + str(deg + 2000) + str(Right_color) + str(Left_color) + '$' # Формирует сообщение на Pyboard
        
        if state == "0" or state  == "Move": # Ожидания кнопки для остановки робота
            if Button == False and time_button + 1 < time.time():
                state = '0'
                deg = rul
                time_button = time.time()
                Right_color = 1
                speed = 0
                max_speed = 0
                min_speed = 0
                Left_color = 1
                print(section)
                print(time_line_to_line)
                print(time_line_to_obj)
                print("  ")
                index()
                print("  ")
                print(section)
    port.write(message.encode('utf-8')) # Отправляет сообщение на Pyboard



    robot.text_to_frame(frame, 'fps = ' + str(fps), 500, 20)
    robot.text_to_frame(frame, 'ii = ' + str(ii) + ' ' + 'state=' + str(state) + ' ' + str(message) + ' ' + str(direction), 20, 20)
    robot.text_to_frame(frame, 'e = ' + str(e) + ' ' + 'sr1=' + str(left_sensor) + ' ' + str(right_sensor) + ' ' + str(Flag_button) + ' ' + str(per) + ' ' + str(rsr) + ' ' + str(gsr), 20, 40)
    robot.text_to_frame(frame, 'yr = ' + str(yred) + ' ' + 'yg=' + str(ygr) + ' ' + str(Objsr) + ' ' + str(Flag_obj_green) + ' ' + str(Flag_obj_red) + ' ' + str(index_section) + ' ' + str(deg) + ' ' + str(Object_red) + ' ' + str(Object_green) + ' ' + str(Button), 20, 60)
    robot.text_to_frame(frame, str(section), 20, 80,(255, 255 , 255))
    # Вывод отладочных даннхы
    robot.set_frame(frame, 40)
