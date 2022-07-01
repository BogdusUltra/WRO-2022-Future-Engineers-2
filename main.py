from pyb import delay, Pin, ADC, Timer, UART, Servo
import machine
import time
import pyb

uart = UART(6, 115200, stop=1)

Right_led_red = Pin('X6', Pin.OUT_PP)
Right_led_green = Pin('X5', Pin.OUT_PP)
Right_led_blue = Pin('X4', Pin.OUT_PP)

Left_led_red = Pin('X3', Pin.OUT_PP)
Left_led_green = Pin('X2', Pin.OUT_PP)
Left_led_blue = Pin('X11', Pin.OUT_PP)
# Инициализация светодиодов

Motor = Pin('X10')
M1 = Pin('Y10', Pin.OUT_PP)
M2 = Pin('Y9', Pin.OUT_PP)
tim = Timer(4, freq=10000)
ms = tim.channel(2, Timer.PWM, pin=Motor)
# Инициализация мотора

Servo1 = pyb.Servo(1)
# Инициализация серводвигателя

inn = ""
message = '000$'

count = 0

ONorOFF = 'off'
speed = 0
rul = 13

flag_start = True

e_old = 0


def motor(sp): # Функция управляющая мотором
    global M1, M2, ms
    if sp < 0: # Если скорость меньше 0, то едем назад
        M1.low()
        M2.high()
    else: # Иначе вперед
        M1.high()
        M2.low()
    ms.pulse_width_percent(abs(sp)) # Управляет скоростью мотора

t = pyb.millis()
# Инициализаця таймера

Right_led_red.high()
Left_led_red.high()
# Включение светодиодов

while True: # Основной цикл программы
    if flag_start: # Если True, то скорость мотора = 0 и серводвигатель ставится в 0
        rul = -13
        motor(0)
        Servo1.angle(rul)

    if uart.any(): # Фильтр, убирающий шум 
        a = chr(uart.readchar())
        if a != '$':
            inn += a
            if len(inn) > 10:
                inn = ''
        else: # Ждем нужного сообщения - 999999999$
            if ONorOFF == 'off':
                if inn == '999999999':
                    ONorOFF = 'on'
                    flag_start = False
                    Left_led_red.low()
                    Right_led_red.low()
                    Right_led_green.high()
                    Left_led_green.high()
                    delay(500)
                    Left_led_green.low()
                    Right_led_green.low()
                    delay(50)
                    Right_led_blue.high()
                    Left_led_blue.high()
                    delay(500)
                    Left_led_blue.low()
                    Right_led_blue.low()
                    delay(50)
            if ONorOFF == 'on':
                try:
                    if len(inn) == 9 and inn != '999999999': # Обрабатываем сообщение
                        speed = int(inn[:3]) - 200 # Первые 3 символа - скорость
                        rul = int(inn[3:7]) - 2000 # Следующие 4 символа - угол поворота серводвигателя
                        Right_color = int(inn[7:8]) # Значение цвета светодиодов
                        Left_color = int(inn[8:9]) # Значение цвета светодиодов
                        # print(serv_deg.read())
                        if Right_color == 1: 
                            Right_led_red.high()
                            Right_led_green.low()
                            Right_led_blue.low()

                        if Left_color == 1:
                            Left_led_red.high()
                            Left_led_green.low()
                            Left_led_blue.low()

                        if Right_color == 2:
                            Right_led_green.high()
                            Right_led_red.low()
                            Right_led_blue.low()

                        if Left_color == 2:
                            Left_led_green.high()
                            Left_led_blue.low()
                            Left_led_red.low()

                        if Right_color == 3:
                            Right_led_blue.high()
                            Right_led_green.low()
                            Right_led_red.low()

                        if Left_color == 3:
                            Left_led_blue.high()
                            Left_led_green.low()
                            Left_led_red.low()

                        if Right_color == 4:
                            Right_led_red.high()
                            Right_led_green.high()
                            Right_led_blue.low()

                        if Left_color == 4:
                            Left_led_red.high()
                            Left_led_green.high()
                            Left_led_blue.low()

                        if Right_color == 0:
                            Right_led_red.low()
                            Right_led_green.low()
                            Right_led_blue.low()

                        if Left_color == 0:
                            Left_led_red.low()
                            Left_led_green.low()
                            Left_led_blue.low()
                        # Условия для зажигания светодиодов разными цветами

                        inn = '' # отчистка сообщения
                        motor(speed) #подаем скорость на функцию
                        Servo1.angle(rul) #подаем угол поворота  на функцию
                except ValueError:
                    print('err')

            inn = '' # отчистка сообщения

# 0 = 1125   100 = 0    -100 = 2815