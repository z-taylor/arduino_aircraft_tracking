import time
import math, numpy as np
from pymata4 import pymata4
from opensky_api import OpenSkyApi

#defining some variables
brngRead=float()
stepsRead=int()
speedRead=int()
destLatRead=float()
destLongRead=float()
userLat=float()
userLong=float()
runProgram=True

#gets bearing between local location and destination
def get_bearing(lat1,lon1,lat2,lon2):
    global brngRead
    lat1=math.radians(lat1)
    lat2=math.radians(lat2)
    lon1=math.radians(lon1)
    lon2=math.radians(lon2)
    dLon = lon2 - lon1
    y = math.sin(dLon) * math.cos(lat2)
    x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon)
    brng = np.rad2deg(math.atan2(y, x))
    brng = round(brng)
    if brng < 0: brng+= 360
    brngRead=brng
    return brng

#calculates the number of steps needed to point in the correct direction
def numOfSteps(dir):
    global stepsRead
    dir1= float(dir)
    num= float(dir1/360)
    steps1= float(2048*num)
    steps2= round(steps1)
    steps= int(steps2)
    stepsRead=steps
    return steps

#calculates the speed the motor will spin at to point the right direction
def motor_speed(numSteps):
    global speedRead
    numSteps=abs(numSteps)
    num1= int(2048/numSteps)
    speed= int(num1*10)
    if speed>100:
        speed= int(10)
        speedRead=speed
        return speed
    else:
        speed1= int(round(speed))
        speed= int(speed1//4)
        speedRead=speed
        return speed

#returns the motor back to the neutral position
def returnToNeutral(speed, steps):
    #set the board to stepper motor control mode
    board.set_pin_mode_stepper(2048, pins)
    #moves the board back to its 0 position
    board.stepper_write(speed, -steps)

#calls the OpenSky api for the long and lat of the requested aircraft
def OpenSkyApiCall(wanted_aircraft):
    global destLatRead
    global destLongRead
    locating=int(0)
    api = OpenSkyApi()
    states = api.get_states()
    for s in states.states:
        callsign_preSPACE= str(s.icao24)
        callsign_withLOWERS= callsign_preSPACE.replace(" ", "")
        callsign= callsign_withLOWERS.upper()
        if callsign != wanted_aircraft and locating==int(1):
            locating= locating+1
            print("Locating...")      
        elif callsign==wanted_aircraft:
            destLat= float(s.latitude)
            destLong= float(s.longitude)
            destLatRead= float(s.latitude)
            destLongRead= float(s.longitude)
            return(destLat, destLong)
    print("not found")
    return

#Defines some paramaters for the arduino board
pins= [8, 10, 9, 11]
board=pymata4.Pymata4()
board.set_pin_mode_stepper(2048, pins)

#primary calculations and functions of the program
def main_calc(pins, inLat, inLong, aircraft):
    #set the board to stepper motor control mode
    board.set_pin_mode_stepper(2048, pins)
    userInput1= str(aircraft)
    userInput2= userInput1.replace(" ", "")
    wanted_aircraft= userInput2.upper()
    #lat & long cooridinates
    myLat, myLong = float(inLat), float(inLong)
    destLat, destLong = OpenSkyApiCall(wanted_aircraft)
    #bearing calculation
    bearing= get_bearing(myLat, myLong, destLat, destLong)
    print(bearing)
    #calculate number of motor steps
    num_steps= numOfSteps(bearing)
    #calculate motor speed
    stepper_speed= motor_speed(num_steps)
    board.set_pin_mode_stepper(2048, pins)
    #moves the stepper motor
    board.stepper_write(stepper_speed, num_steps)
    #turn of power to the motor to stop it from overheating
    board.set_pin_mode_digital_output(8)
    board.digital_write(8, 0)
    board.set_pin_mode_digital_output(9)
    board.digital_write(9, 0)
    board.set_pin_mode_digital_output(10)
    board.digital_write(10, 0)
    board.set_pin_mode_digital_output(11)
    board.digital_write(11, 0)

#a function for updating the location of the aircraft
def main_calc_update(pins, inLat, inLong, aircraft):
    #set the board to stepper motor control mode
    board.set_pin_mode_stepper(2048, pins)
    userInput1= str(aircraft)
    userInput2= userInput1.replace(" ", "")
    wanted_aircraft= userInput2.upper()
    #lat & long cooridinates
    myLat, myLong = float(inLat), float(inLong)
    destLat, destLong = OpenSkyApiCall(wanted_aircraft)
    #bearing calculation
    bearing= get_bearing(myLat, myLong, destLat, destLong)
    print(bearing)
    #storing the current number of motor steps for another calculation
    steps1=stepsRead
    #calculate number of motor steps
    steps2= numOfSteps(bearing)
    #calculates the motor steps for updating the position
    num_steps=(steps2-steps1)
    #ends the function if the number of steps is 0 and the motor will not move, as this will cause an error in the motor speed calculation function due to dividing by 0
    if num_steps==0:
        return
    #calculate motor speed
    stepper_speed= motor_speed(num_steps)
    board.set_pin_mode_stepper(2048, pins)
    board.stepper_write(stepper_speed, num_steps)
    #turn of power to the motor to stop it from overheating
    board.set_pin_mode_digital_output(8)
    board.digital_write(8, 0)
    board.set_pin_mode_digital_output(9)
    board.digital_write(9, 0)
    board.set_pin_mode_digital_output(10)
    board.digital_write(10, 0)
    board.set_pin_mode_digital_output(11)
    board.digital_write(11, 0)

#user interface, this is what the user will interact with to use the program
def UI(pins, destLat, destLong, speed, steps, brng):
    global runProgram
    global userLat
    global userLong
    global set_aircraft
    print()
    print("Available functions include:   Show variable, set aircraft, change aircraft, update aircraft location, set my position, return to neutral, and exit program. (not case sensitive)")
    funct1= input(str("Which function would you like to use?   "))
    funct2= funct1.replace(" ", "")
    funct= funct2.lower()
    if funct==str("showvariable"):
        print("Available variables to show include:   pins, destLat, destLong, myLat, myLong, speed, steps, and brng.")
        var1= input(str("Which variable would you like to see?   "))
        var2= var1.replace(" ", "")
        var= var2.lower()
        if var=="pins":
            print(pins)
            print("If 'None', '0', or 'NaN' was displayed, the variable does not contain anything yet.")
        elif var=="destlat":
            print(destLatRead)
            print("If 'None', '0', or 'NaN' was displayed, the variable does not contain anything yet.")
        elif var=="destlong":
            print(destLongRead)
            print("If 'None', '0', or 'NaN' was displayed, the variable does not contain anything yet.")
        elif var=="mylat":
            print(userLat)
            print("If 'None', '0', or 'NaN' was displayed, the variable does not contain anything yet.")
        elif var=="mylong":
            print(userLong)
            print("If 'None', '0', or 'NaN' was displayed, the variable does not contain anything yet.")
        elif var=="speed":
            print(speedRead)
            print("If 'None', '0', or 'NaN' was displayed, the variable does not contain anything yet.")
        elif var=="steps":
            print(stepsRead)
            print("If 'None', '0', or 'NaN' was displayed, the variable does not contain anything yet.")
        elif var=="brng":
            print(brngRead)
            print("If 'None', '0', or 'NaN' was displayed, the variable does not contain anything yet.")
        else:
            print(var, "is not a valid variable, please try another.")
    elif funct==str("setaircraft") or funct==str("set"):
        if userLat==0 and userLong==0:
            userLat=input("Type in your lattitude coordinate here:   ")
            userLong=input("Type in your longitude coordinate here:   ")
            set_aircraft=input(str("Type in the 24-bit ICAO address of the aircraft you want to track here:   "))
            main_calc(pins, userLat, userLong, set_aircraft)
        else:
            set_aircraft=input(str("Type in the 24-bit ICAO address of the aircraft you want to track here:   "))
            main_calc(pins, userLat, userLong, set_aircraft)
    elif funct==str("changeaircraft") or funct==str("change"):
        returnToNeutral(speed, steps)
        set_aircraft=input(str("Type in the 24-bit ICAO address of the aircraft you want to track here:   "))
        main_calc(pins, userLat, userLong, set_aircraft)
    elif funct==str("updateaircraftlocation") or funct==str("update"):
        main_calc_update(pins, userLat, userLong, set_aircraft)
    elif funct==str("setmyposition"):
        userLat=input("Type in your lattitude coordinate here:   ")
        userLong=input("Type in your longitude coordinate here:   ")
    elif funct==str("returntoneutral"):
        returnToNeutral(speed, steps)
    elif funct==str("exitprogram"):
        returnToNeutral(speed, steps)
        time.sleep(30)
        board.set_pin_mode_digital_output(8)
        board.digital_write(8, 0)
        board.set_pin_mode_digital_output(9)
        board.digital_write(9, 0)
        board.set_pin_mode_digital_output(10)
        board.digital_write(10, 0)
        board.set_pin_mode_digital_output(11)
        board.digital_write(11, 0)
        runProgram=False
    else:
        print("That is not a valid function. Please check you spelling and try again.")

#keeps the program running until the user decides to terminate the program
while runProgram==True:
    UI(pins, destLatRead, destLongRead, speedRead, stepsRead, brngRead)
    time.sleep(1)

#not including comments, this program uses 206 lines of code, or 193 excluding line breaks as well