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
time_for_sensor		= 6	# 6 seconds
time_to_sleep		= 2     # 2 second 

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


#Send environment summary to LCD display
def push_to_LCD_summary():
        #Printing summary info
        l = light_adjustment()
        t = temperature_adjustment()
        d = distance_adjustment()
        h = humidity_adjustment()
        
        setRGB(0,0,0)
        setText("Time: " + curr_time)
        time.sleep(2)
        setText("Temp: " + t + "       " + "Humidity: " + h)
        time.sleep(2)
        setText("Distance: " + d + "     " + "Light: " + l)
        time.sleep(2)

#Send environment data to LCD display
def push_to_LCD():
        #Print values
        l = str(light)
        d = str(distance)
        t = str(tempf)
        h = str(humidity)
        
        setRGB(0,0,0)
        setText("Time: " + curr_time)
        time.sleep(2)
        setText("Temp: " + t + "      " + "Humidity: " + h)
        time.sleep(2)
        setText("Distance: " + d + "     " + "Light: " + l)
        time.sleep(2)
        
#Create log file
def create_logs():
        f=open(log_file, 'a')
        f.write("%s,%d,%d,%.2f,%.2f;\n" %(curr_time, light, distance, tempf, humidity))
        f.close()        


#Adjust distance conditions
def distance_adjustment():
        if distance > 50 and distance < 70:
                print ("Distance: Normal")
                dd = "Normal"
                return dd
                
        elif distance < 50:
                print ("Distance: Full")
                dd = "Full"
                return dd
                
        elif distance > 70 and distance < 100:
                print ("Distance: Low")
                dd = "Low"
                return dd
                
        elif distance > 100:
                print ("Distance: Empty")
                dd = "Empty"
                return dd
                
        else:
                print ("Ultrasonic Ranger Error, Unexpected Value")
                dd = "Error"
                return dd
                
#Adjust temperature conditions (Turn fan ON/OFF)
def temperature_adjustment():
        #Return -1 in case of bad temp/humidity sensor reading
        #HT sensor sometimes gives nan
        if math.isnan(temp):
                print (-1)

        else:
                if tempf > 75:
                        print ("Temperature: High") #Turn fan ON
                        tt = "High"
                        return tt
                        #grovepi.digitalWrite(relay_pin_1,1)

                elif tempf > 65 and tempf < 75:
                        print ("Temperature: Normal") #Turn fan OFF
                        tt = "Normal"
                        return tt
                        #grovepi.digitalWrite(relay_pin_1,0)
                        
                elif tempf < 65:
                        print ("Temperature: Low") #Turn fan OFF
                        tt = "Low"
                        return tt
                        #grovepi.digitalWrite(relay_pin_1,0)

                else:
                        print ("Temperature Error, Unexpected Value")
                        tt = "Error"
                        return tt

#Adjust humidity conditions (Turn fan ON/OFF)
def humidity_adjustment():
        #Return -1 in case of bad temp/humidity sensor reading
        #HT sensor sometimes gives nan
        if math.isnan(humidity):
                print (-1)

        else:
                if humidity > 65:
                        print ("Humidity: High") #Turn fan ON
                        hh = "High"
                        return hh
                        #grovepi.digitalWrite(relay_pin_1,1)

                elif humidity > 50 and humidity < 65:
                        print ("Humidity: Normal") #Turn fan OFF
                        hh = "Normal"
                        return hh
                        #grovepi.digitalWrite(relay_pin_1,0)
                        
                elif humidity < 50:
                        print ("Humidity: Low") #Turn fan OFF
                        hh = "Low"
                        return hh
                        #grovepi.digitalWrite(relay_pin_1,0)

                else:
                        print ("Humidity Error, Unexpected Value")
                        hh = "Error"
                        return hh

#Adjust light conditions
def light_adjustment():
        if light > 400 and light < 500:
                print ("Light: Normal")
                ll = "Normal"
                return ll

        elif light < 400:
                print ("Light: Low")
                ll = "Low"
                return ll

        elif light > 500:
                print ("Light: High")
                ll = "High"
                return ll

        else:
                print ("Light Sensor Error, Unexpected Value")
                ll = "Error"
                return ll

#Increments sensor measurements, outputs results, & adjusts conditions        
while True:
        curr_time_sec = int(time.time())
        try:
                #If time interval has passed take new light reading
                if curr_time_sec - last_read_sensor > time_for_sensor:
                        [light, distance, temp, humidity] = read_sensor()
                        #Convert Celcius to Fahrenheit
                        tempf = round((temp * 1.8) + 32, 2)

                        #Print conditions to console
                        curr_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        print (("Time: %s\nLight: %d\nDistance: %d\nTemperature: %.2f F\nHumidity: %.2f %%\n" %(curr_time, light, distance, tempf, humidity)))
                        
                        #Save sensor reading to CSV file
                        create_logs()
                
                        #Make environment adjustments
                        #Distance
                        distance_adjustment()
                        #Light
                        light_adjustment()
                        #Temperature
                        temperature_adjustment()
                        #Humidity
                        humidity_adjustment()

                        #Push environment data summary to LCD display
                        push_to_LCD_summary()

                        #Push environment data to LCD display
                        push_to_LCD()

                        #Update the last read time
                        last_read_sensor=curr_time_sec

                #Slow down the loop
                time.sleep(time_to_sleep)
              
        except KeyboardInterrupt: #Turn LED off before stopping
                grovepi.digitalWrite (led,0)
                setRGB (0,0,0)
                setText ("")
                break

        except IOError: #Print if sensor error
                print ("Error")

#Light interval (vegetative, 16hrs light / 8hrs dark)
while True:
        current_time = int(time.time())
        wait_1 = 57600  #16hr in seconds
        wait_2 = 28800  #8hr in seconds
        start = 1
        last_time = int(time.time())   

        if start % 2 == 0:

                if current_time - last_time > wait_1: #Turns light OFF
                        print ("Turn OFF")
                        #grovepi.digitalWrite(relay_pin_2,0)
                        start = start + 1
                        last_time = curr_time

        elif start % 2 != 0:

                if current_time - last_time > wait_2: #Turns light ON
                        print ("Turn ON")
                        #grovepi.digitalWrite(relay_pin_2,1)
                        start = start + 1
                        last_time = current_time

        else:
                print ("Error")

#Light interval (flowering, 12hrs light / 12hrs dark)
#while True:
#        current_time = int(time.time())
#        wait_1 = 43200  #12hrs in seconds
#        wait_2 = 43200  #12hrs in seconds
#        start = 1
#        last_time = int(time.time())
#
#        if start % 2 == 0:
#
#                if current_time - last_time > wait_1: #Turns light OFF
#                print ("Turn OFF")
#                #grovepi.digitalWrite(relay_pin_2,0)
#                start = start + 1
#                last_time = curr_time
#
#        elif start % 2 != 0:
#
#                if current_time - last_time > wait_2: #Turns light ON
#                        print ("Turn ON")
#                       #grovepi.digitalWrite(relay_pin_2,1)
#                       start = start + 1
#                       last_time = current_time
#
#        else:
#                print ("Error")

#Watering interval (15 minutes ON, 45 minutes OFF)
while True:
        current_time = int(time.time())
        wait_1 = 900  #15 minutes in seconds
        wait_2 = 2700  #45 minutes in seconds
        start = 1
        last_time = int(time.time())   

        if start % 2 == 0:

                if current_time - last_time > wait_1: #Turns water OFF
                        print ("Turn OFF")
                        #grovepi.digitalWrite(relay_pin_3,0)
                        start = start + 1
                        last_time = curr_time

        elif start % 2 != 0:

                if current_time - last_time > wait_2: #Turns water ON
                        print ("Turn ON")
                        #grovepi.digitalWrite(relay_pin_3,1)
                        start = start + 1
                        last_time = current_time

        else:
                print ("Error")
