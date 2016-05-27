#!/usr/bin/env python
#
#Garden Monitor Project
#Reads the data from a variety of sensors and modulates garden conditions
#
#       Connections to GrovePi:
#           Digital Temperature & Humidity Sensor   - Port D2
#           Analog Light Sensor                     - Port A1
#           Digital Ultrasonic Ranger Sensor        - Port D3
#           Digital LED                             - Port D4
#           I2C RGB Backlight LCD                   - Port I2C-1
#           Digital Relay                           - Port D8

import time
import grovepi
import subprocess
import math
from grove_rgb_lcd import *

#Import sensor/relay functions


#Analog sensor port number
light_sensor = 1

#Digital sensor port number
temp_humidity_sensor = 2
ultrasonic_ranger = 3
led = 4
relay_pin_1 = 5
relay_pin_2 = 6
relay_pin_3 = 7
relay_pin_4 = 8

#temp_humidity_sensor type
#Grove starter kit comes with the blue sensor
blue = 0

#time_for_sensor = 1*60*60	# 1 hr
#test timings
time_for_sensor		= 4	# 4 seconds
time_to_sleep		= 1     # 1 second 

#Initial Sensor Read
last_read_sensor = int(time.time())

log_file="plant_monitor_log.csv"

#Set Pin Modes (Input/Output)
grovepi.pinMode(light_sensor, "INPUT")
grovepi.pinMode(temp_humidity_sensor, "INPUT")
grovepi.pinMode(ultrasonic_ranger, "INPUT")
grovepi.pinMode(led, "OUTPUT")
grovepi.pinMode(relay_pin_1, "OUTPUT")
grovepi.pinMode(relay_pin_2, "OUTPUT")
grovepi.pinMode(relay_pin_3, "OUTPUT")
grovepi.pinMode(relay_pin_4, "OUTPUT")

#Read the data from the sensors
def read_sensor():
        try:
                light = grovepi.analogRead(light_sensor)
                distance = grovepi.ultrasonicRead(ultrasonic_ranger)
                [temp, humidity] = grovepi.dht(temp_humidity_sensor, blue)
                #Return -1 in case of bad temp/humidity sensor reading
                if math.isnan(temp) or math.isnan(humidity):
                        return [-1, -1, -1, -1]
                return [light, distance, temp, humidity]
        
        except IOError as TypeError:
                return [-1, -1, -1, -1]


#Send environment conditions to LCD display
def push_to_LCD():
        l = str(light)
        d = str(distance)
        t = str(tempf)
        h = str(humidity)
        setRGB(0,0,0)
        setText("Time: " + curr_time)
        time.sleep(1)
        setText("Temp: " + t + "      " + "Humidity: " + h)
        time.sleep(1)
        setText("Distance: " + d + "     " + "Light: " + l)


#Create log file
def create_logs():
        f=open(log_file, 'a')
        f.write("%s,%d,%d,%.2f,%.2f;\n" %(curr_time, light, distance, tempf, humidity))
        f.close()        


#Adjust distance conditions
def distance_adjustment():
        if distance > 50 and distance < 70:
                print ("Normal")

        elif distance < 50:
                print ("Full")

        elif distance > 70:
                print ("Empty")

        else:
                print ("Ultrasonic Ranger Error, Unexpected Value")

#Adjust temperature conditions (Turn fan ON/OFF)
def temperature_adjustment():
        #Return -1 in case of bad temp/humidity sensor reading
        #HT sensor sometimes gives nan
        if math.isnan(temp):
                print (-1)

        else:
                if tempf > 85:
                        print ("High Temperature") #Turn fan ON
                        #grovepi.digitalWrite(relay_pin_1,1)

                elif tempf > 60 and tempf < 85:
                        print ("Normal Temperature")
                
                elif tempf < 60:
                        print ("Low Temperature") #Turn fan OFF
                        #grovepi.digitalWrite(relay_pin_1,0)

                else:
                        print ("Temperature Error, Unexpected Value")


#Adjust humidity conditions (Turn fan ON/OFF)
def humidity_adjustment():
        #Return -1 in case of bad temp/humidity sensor reading
        #HT sensor sometimes gives nan
        if math.isnan(humidity):
                print (-1)

        else:
                if humidity > 80:
                        print ("High Humidity") #Turn fan ON
                        #grovepi.digitalWrite(relay_pin_1,1)

                elif humidity > 50 and humidity < 80:
                        print ("Normal Humidity")

                elif humidity < 50:
                        print ("Low Humidity") #Turn fan OFF
                        #grovepi.digitalWrite(relay_pin_1,0)

                else:
                        print ("Humidity Error, Unexpected Value")


#Adjust light conditions
def light_adjustment():
        if light > 400 and light < 500:
                print ("Normal Light")

        elif light < 400:
                print ("Low Light")

        elif light > 500:
                print ("High Light")

        else:
                print ("Light Sensor Error, Unexpected Value")


#Increments sensor measurements, outputs results, & adjusts conditions        
while True:
        curr_time_sec = int(time.time())
        try:
                #If time interval has passed take new light reading
                if curr_time_sec - last_read_sensor > time_for_sensor:
                        [light, distance, temp, humidity] = read_sensor()
                        curr_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        #Convert Celcius to Fahrenheit
                        tempf = round((temp * 1.8) + 32, 2)
                        print (("Time: %s\nLight: %d\nDistance: %d\nTemperature: %.2f F\nHumidity: %.2f %%\n" %(curr_time, light, distance, tempf, humidity)))

                        #Push environment data to LCD display
                        push_to_LCD()
                        
                        #Save sensor reading to CSV file
                        create_logs()
                
                        #Update the last read time
                        last_read_sensor=curr_time_sec

                        #Make environment adjustments
                        #Distance
                        distance_adjustment()
                        #Light
                        light_adjustment()
                        #Temperature
                        temperature_adjustment()
                        #Humidity
                        humidity_adjustment()
                        
                #Slow down the loop
                time.sleep(time_to_sleep)
              
        except KeyboardInterrupt: #Turn LED off before stopping
                grovepi.digitalWrite (led,0)
                setRGB (0,0,0)
                setText ("")
                break

        except IOError: #Print if sensor error
                print ("Error")

