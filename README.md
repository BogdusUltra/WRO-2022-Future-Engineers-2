URL to youtube - https://youtu.be/OjZ5FfyUcak

# Description of the algorithms
The ![main.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/main.py) is a separate program. It resides on the pyboard. It exchanges data packets with ![qualification.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/qualification.py) or ![final.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/final.py) (depending on which program is running on the Raspberry Pi) via UART. The pyboard processes the received data and depending on the values that were in the data packet, it changes the angle of the servo, the speed of the motors and changes the colour of the RGB LEDs (headlights).

![RobotAPI.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/RobotAPI.py) is a special class that creates our robot as an object, it can read out the image from the camera and display it on the laptop screen.

![start_robot.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/start_robot.py) is a program that creates a separate application that can be used to communicate with the Raspberry Pi via the Wi-Fi network. To do this, you need to connect to the Raspberry Pi via Wi-Fi (in our case "Car3"). Then launch the application itself and by pressing the "Connect to robot" button select the ip address of our Raspberry Pi. There are several main functions in the application interface.
1. "Load start": allows you to select the software to load and run on your Raspberry Pi.
2. "Start": starts the last programme downloaded to the Raspberry Pi.
3. "Stop": finishes execution of the program on Raspberry Pi.
4. "Video": creates a separate window and displays the camera image there. 

The application also reports errors in the program, if any.


![autostart.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/autostart.py) is a programme that runs automatically as soon as RaspberryPi is switched on. It executes any program whose name appears in the code after import.
For any program (![qualification.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/qualification.py) and ![final.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/final.py) in our case) to run when Raspberry Pi is switched on, we need to load it with ![start_robot.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/start_robot.py) and then load ![autostart.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/autostart.py).


![qualification.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/qualification.py) is the program for the qualification stage. It is located on the Raspberry Pi. The program has 3 main positions(variable "state"):
1) "0";
2) "move";
3) "finish".

From the beginning the program is in state "0", it just waits for the information that the button has been pressed. If the button is pressed, the program moves to state "move". When the program moves to state "move" the main algorithm is started. The program processes the camera image using the openCV library. It recognizes the black walls of the field and determines how much the robot has deviated from the planned route, it detects an error. Next, we calculate the angle by which to turn the servomotor using the formulas: "u = e * kp + (e - e_old) * kd" "deg = rul - u",
where "deg" is the required angle of servo motor rotation; "rul" is the initial angle of servo motor rotation at which the wheels are aligned; "u" is the difference between "rul" and "deg"; "e" is the error; "kp" is the proportional control coefficient; "kd" is the differential control coefficient; "e_old" is the past error("e") which is updated with each iteration of the cycle. Also, in this state the program counts how many turns the robot has made. The sensors can not recognize a turn, but they can recognize the blue and orange lines, they are on the turns. The headlights light up in the same colour as the line seen by the sensor. After 12 turns, i.e. 3 laps, the program switches to state "finish". State "finish" is the final phase of the program. In this state, just like in state "move", the program calculates the error and aligns the robot. But after a certain time it sets the value of the speed variable to 0. After the mathematical calculations and regardless of the state the programme is in, we send the values "deg" and "speed" (the speed variable, which like the "deg" variable can change throughout the programme) to the pyboard via UART. This data is received by the ![main.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/main.py) program.

![final.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/final.py) is the program for the final stage of the competition. It resides on the Raspberry Pi.
final.py just like qualification.py waits for the button to be pressed, aligns the robot to the center and counts the laps traveled, it has the same number of states. But it also allows the robot to drive around traffic signs - green and red parallelepipeds. The robot needs to bypass green objects on the left side and red ones on the right.
To do this, sensors have been added that look for red and green objects. If the sensor finds a green object, the program writes in the variables "gsr" and "ygr" the position of its upper left corner by x and y coordinate respectively. And if the sensor detects a red object, it will similarly write the position of its upper right corner into the variables "rsr" and "yred". If the sensor sees only a red object, the program will write the value True to the "Flag_obj_red" variable and if it sees only green, it will write the value to the "Flag_obj_green" variable. But if the sensor sees two objects at once it writes the value "True" in the variable of the object that is closer.
If any of these variables is True, the program calculates a new error that will allow the robot to align between the desired wall and the object.
With this algorithm, the robot successfully bypasses the objects on the right sides. The headlights also light up in the same colour as the parallelepipeds that the sensor sees.



# Connecting to the pyboard.
We need to install the main.py file on the pyboard. To do this we need to connect pyboard to a laptop via a miniUSB wire. Open explorer and move the main.py file to pyboard and click "replace".

# Connecting to the Raspberry Pi and loading programs.
First we need to power up the Raspberry Pi and wait for it to fully boot up. The Raspberry Pi will start its Wi-Fi hotspot and we need to connect to it. The Wi-Fi network on our Raspberry Pi is called "Car3".

![1](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/readme_images/1.jpg)

After connecting to the Wi-Fi, start PyCharm and run the program ![start_robot.py](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/start_robot.py).

![2](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/readme_images/2.jpg)

The special application opens and in its upper right corner there is a "Connect to robot" button. You need to click on it and select the suggested ip address.

![3](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/readme_images/3.jpg)

We have connected to the Raspberry Pi.

![4](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/readme_images/4.jpg)

Now we can load the programs there.
To do that we need to click on the "load start" button. A file selection window will open, select the required program file and click on "open". 

![5](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/readme_images/5.jpg)

The application file has been uploaded and started automatically.

![6](https://github.com/BogdusUltra/WRO-2022-Future-Engineers/blob/main/readme_images/6.jpg)



# Running a programme on the Raspberry Pi.
The programmes will start as soon as they are downloaded to the Raspberry Pi using the laptop. But if the robot is restarted, the programme will not start.
In order to ensure that the program we need is started automatically after the robot is switched on, the autostart.py program must also be preloaded on the Raspberry Pi.
