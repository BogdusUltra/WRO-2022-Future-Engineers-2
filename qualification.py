from mimetypes import guess_all_extensions
from operator import index
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
state = '0'
ii = ''
fps = 0
fps1 = 0
fps_time = 0

xright21, yright21 = 390, 230
xright22, yright22 = 640, 270

xleft11, yleft11 = 0, 230
xleft12, yleft12 = 250, 270

xright41, yright41 = 590, 200
xright42, yright42 = 640, 230

xleft31, yleft31 = 0, 200
xleft32, yleft32 = 50, 230

xBl1, yBl1 = 290, 340
xBl2, yBl2 = 320, 350

xOl1, yOl1 = 320, 340
xOl2, yOl2 = 350, 350
# Инициализация констант для координат областей интереса

e = 0
count = 0
x1 = 1130
x, y = 300, 200
w, h = 40, 80
a = ''
t_cube = 0.2
per = 0
temp = 0
t_y = 0
# Инициализация доп. отладочных переменных

speed = 40
max_speed = 40
min_speed = 40
# Инициализация констант для скорости движения робота

kp = 0.5
kd = 0.5
e_old = 0
# Инициализация констант для PD регулятора

Right_color = 1
Left_color = 1
# Инициализация констант для светодиодов

rul = 0
deg = 0
sp = 0
# Инициализация констант для управления серводвигателем

tper = time.time()
t_obj =time.time()
t_red = time.time()
t_green = time.time()
t_led = time.time()
time_button = time.time()
# Инициализация таймеров

lowBl = np.array([93, 64, 21])
upBl = np.array([112, 255, 97]) #Проверить

lowOl = np.array([5, 70, 57])
upOl = np.array([23, 177, 148]) #Проверить

lowObjgreen = np.array([70, 200, 58])
upObjgreen = np.array([85, 255, 138]) #Проверить

lowObjred = np.array([0, 142, 6])
upObjred = np.array([10, 255, 255]) #Проверить
# Инициализация констант для hsv

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
    global max2, yBl1, yBl2, xBl1, xBl2, t, per, sr, state, direction, Flag_line_blue, Flag_line
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

def orange_line(): # Функция определения оранжевой линии
    global max2, yOl1, yOl2, xOl1, xOl2, t, per, sr, state, direction, Flag_line_orange, Flag_line
    line = frame[yOl1:yOl2, xOl1:xOl2] # Забираем из изображения с камеры область интереса
    cv2.rectangle(frame, (xOl1, yOl1), (xOl2, yOl2), (0, 0, 255), 2) # Обводим датчик оранжевой линии
    hsv = cv2.cvtColor(line, cv2.COLOR_BGR2HSV) # Переводим изображение из RGB в HSV
    mask = cv2.inRange(hsv, lowOl, upOl) # С помощью inRange мы находим маску оранжевого на изображении
    gray1 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) # Переводим изображение из серого в RGB
    frame[yOl1:yOl2, xOl1:xOl2] = gray1 # Отрисовываем датчик на экран
    imd, contours, h = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE) # Находим контуры по маске mask
    max2 = 0
    for contor in contours:
        x1, y1, w1, h1 = cv2.boundingRect(contor) # Координаты, высота и ширина найденного контура
        a1 = cv2.contourArea(contor) # Площадь найденного контура
        if a1 > 100: # Убираем шумы по площади
            cv2.rectangle(line, (x1, y1), (x1 + w1, y1 + h1), (0, 255, 0), 2) # Обводим контур
            Flag_line_orange = True
            Flag_line = True
            # Поднятие флагов при определении линии
            direction = "Orange"
            # Изменение переменной направления


while True: # Основной цикл программы 
    Button = (IO.input(18)) # считывание кнопки для запуска программы
    frame = robot.get_frame(wait_new_frame=1) #Получаем кадр с камеры на роботе
    key = robot.get_key() # Считываение кнопок с клавиатуры для ручного управление
    if key == 27: # Переход в основное состояние, в котором робот обруливает кубики
        state = "Move"
        speed = 40
        max_speed = 40
        min_speed = 40


    if t_led + 0.5 < time.time(): # Изменение цвета светодиодов
        Right_color = 1
        Left_color = 3
    elif t_led + 1 < time.time():
        Right_color = 2
        Left_color = 2
    elif t_led + 1.5 < time.time():
        Left_color = 1
        Right_color = 3
    
    fps1 += 1 # Счётчик кадров в секунду
    if time.time() > fps_time + 1:
        fps_time = time.time()
        fps = fps1
        fps1 = 0

    if state == '0': # Состояние "0" - это ожидание загрузки робота и нажатия на кнопку
        if Flag_button == False:
            message = '999999999$'
        else:
            message = str(0 + 200) + str(rul + 2000) + str(Right_color) + str(Left_color) + '$' # Формирует сообщение на Pyboard (Скорость мотора, угол поворота серводвигателя, цвет светодиодов)
        if Button == False and time_button + 1 < time.time():
            state = 'Move' # Переход в состояние основной программы
            direction = 'None' # Направление движения робота (Orange или Blue) в данном случае None, так как робот еще не начал движение
            Flag_button = True
            time_button = time.time()
        if Button:
            pass

    if state != '0' and state != 'Stop': # Состояние ручного управления
        if keyboardcontrol == 'On':
            sp += 1
            key = robot.get_key()
            if key != -1:
                sp = 0
                print(key) # Считываение кнопок с клавиатуры для ручного управление
                if key == 87:
                    speed = 35
                if key == 83:
                    speed = -35
                if key == 65:
                    deg += 50
                if key == 68:
                    deg -= 50
            if sp > 10:
                speed = 0




        if state == "Move": # Основное состояние программы, в ней робот едет по кругу
            Flag_line = False
            Flag_line_blue = False
            Flag_line_orange = False
            # Каждую итерацию Цикла все основные перменные
            black_line() # Функция для езды по стенам

            if direction == "Blue": # В зависимости от направление выключается один из датчиков линии
                blue_line()

            elif direction == "Orange":
                orange_line()
            else: # Иначе работают оба 
                blue_line()
                orange_line()

            e = left_sensor - right_sensor # Вычисление ошибки
            if -5 < e < 5: # Фильтр на маленькие шумы
                e = 0
            u = e * kp + (e - e_old)*kd # pd регулятор

            deg = int(rul - u) # Записываем в переменную deg нужный угол поворота серводвигаетлся
            if deg < -45: # Ограничение угла поворота серводвигателя
                deg = -45
                
            if deg > 45: # Ограничение угла поворота серводвигателя
                deg = 45

            e_old = e # Перезаписываем старую ошибку

            if right_sensor == 0: # Если на правом датчки ничего нет, то мы поворачиваем направо
                deg = -35

            if left_sensor == 0: # Если на левом датчки ничего нет, то мы поворачиваем налево
                deg = 35
                
            if Flag_line and tper + 0.5 < time.time(): # Подсчёт перекрестков
                    per += 1
                    tper = time.time()


            if per // 4 == 3: # Условие перехода в состояние финиша 
                state = "Finish"
                t_finish = time.time()
            

        if state == "Finish": # Состояние финиша, в нем робот едет некоторое время, потом останавливается
            if t_finish + 0.9 > time.time():
                black_line() # Функция для езды по стенам
                e = left_sensor - right_sensor # Вычисление ошибки
                if -5 < e < 5: # Фильтр на маленькие шумы
                    e = 0

                u = e * kp + (e - e_old)*kd # pd регулятор

                deg = int(rul - u) # Записываем в переменную deg нужный угол поворота серводвигаетлся
                if deg < -50: # Ограничение угла поворота серводвигателя
                    deg = -50
                    
                if deg > 50: # Ограничение угла поворота серводвигателя
                    deg = 50

                e_old = e # Перезаписываем старую ошибку

                if right_sensor == 0: # Если на правом датчки ничего нет, то мы поворачиваем направо
                    deg = -35

                if left_sensor == 0:  # Если на левом датчки ничего нет, то мы поворачиваем налево
                    deg = 38
                

    
                
            else: # Когда время выйдет робот остановится и поставит колеса в нулевое положение
                speed = 0
                max_speed = 0
                min_speed = 0
                deg = rul            
            


        deg = -(deg + 13) # Инвертирование руля
        message = str(speed + 200) + str(deg + 2000) + str(Right_color) + str(Left_color) + '$' # Формирует сообщение на Pyboard
        speed = max_speed  
        if Button == False and time_button + 1 < time.time(): # Ожидания кнопки для остановки робота
            state = '0'
            deg = rul
            time_button = time.time()



        # if robot.get_key() == 50:
        #     keyboardcontrol = "On" 
    # if ii == 'B=0' and Flag_start and time_button + 0.5 > time.time():
    #     time_button = time.time()
    #     speed = 0
    #     Flag_start = False
    #     deg = rul
    #     state = 'Stop'
    port.write(message.encode('utf-8')) # Отправляет сообщение на Pyboard


    robot.text_to_frame(frame, 'fps = ' + str(fps) + ' ' + str(Button), 500, 20)
    # robot.text_to_frame(frame, 'ii = ' + str(ii) + ' ' + 'state=' + str(state) + ' ' + str(message) + ' ' + str(direction) + ' ' + str(deg), 20, 20)
    robot.text_to_frame(frame, 'e = ' + str(e) + ' ' + str(left_sensor) + ' ' + str(right_sensor) + ' ' + str(Flag_button) + ' ' + str(per), 20, 40)
    # robot.text_to_frame(frame, 'yr = ' + str(yred) + ' ' + 'yg=' + str(ygr) + ' ' + str(Objsr) + ' ' + str(Flag_obj_green) + ' ' + str(Flag_obj_red), 20, 60)
    # Вывод отладочных даннхы
    robot.set_frame(frame, 40)