# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 14:32:32 2022

@author: Hubert COSTE (CMI Aoustique et vibrations - Le Mans université)
"""
import RPi.GPIO as io
io.setmode(io.BCM)
import sys, tty, termios, time
import matplotlib.pyplot as plt
import numpy as np



################################
# Pins used for the stepper motor
################################
motor_step_pin_1 = 14
motor_direction_pin_1 = 15
motor_step_pin_2 = 23
motor_direction_pin_2 = 24

io.setup(motor_direction_pin_1, io.OUT)
io.setup(motor_step_pin_1, io.OUT)
io.setup(motor_direction_pin_2, io.OUT)
io.setup(motor_step_pin_2, io.OUT)




#######################################
#Delay (influence the rotational speed)
#######################################

delay1 = 1e-6           #fast : default
delay2 = 1e-3           #slow

#only for sine generation
Ts=0.0053     #sampling period (between two instructions)
Fs=1/Ts




#################
# Wave amplitude
#################

pulses_per_rev = 1600        # This can be configured on the driver using the DIP-switches
pulses_per_rev_lin =int(pulses_per_rev/4) #amplitude of linear pulses
pulse_add = 1/4 #added rotation (for kink and antikink generation)




######
#Getch
######
def getch():
    """
    # The getch method can determine which key has been pressed
    # by the user on the keyboard by accessing the system files
    # It will then return the pressed key as a variable
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch




##########
#Functions
###########
# This section of code defines the methods used to determine
# whether the stepper motor needs to spin forward or backwards. 
# Different directions are acheived by setting the
# direction GPIO pin to true or to false. 

#Just one step
def step_once_both(delay=delay1):
    io.output(motor_step_pin_1, True)
    io.output(motor_step_pin_2, True)
    time.sleep(delay)
    
    io.output(motor_step_pin_1, False)
    io.output(motor_step_pin_2, False)
    time.sleep(delay)
    
def step_once_1(delay=delay1):
    io.output(motor_step_pin_1, True)
    time.sleep(delay)
    io.output(motor_step_pin_1, False)
    time.sleep(delay)
    
def step_once_2(delay=delay1) :
    io.output(motor_step_pin_2, True)
    time.sleep(delay)
    io.output(motor_step_pin_2, False)
    time.sleep(delay)
    
    
#Forward   
def step_forward_both(delay=delay1): #Motors 1 and 2
    io.output(motor_direction_pin_1, True)
    io.output(motor_direction_pin_2, True)
    time.sleep(delay)
    step_once_both()

def step_forward_1(delay=delay1) : #Motor 1
    io.output(motor_direction_pin_1, True)
    time.sleep(delay)
    step_once_1()

def step_forward_2(delay=delay1) : #Motor 2
    io.output(motor_direction_pin_2, True)
    time.sleep(delay)
    step_once_2()


#Reverse
def step_reverse_both(delay=delay1): #Motors 1 and 2
    io.output(motor_direction_pin_1, False)
    io.output(motor_direction_pin_2, False)
    time.sleep(delay)
    step_once_both()
    
def step_reverse_1(delay=delay1): #Motor 1
    io.output(motor_direction_pin_1, False)
    time.sleep(delay)
    step_once_1()
    
def step_reverse_2(delay=delay1): #Motor 2
    io.output(motor_direction_pin_2, False)
    time.sleep(delay)
    step_once_2()    


#ONLY FOR SINE GENERATION
def step_once():
    io.output(motor_step_pin_2, True)
    io.output(motor_step_pin_2, False)  
    
def step_forward() :
    io.output(motor_direction_pin_2, True)
    step_once()

def step_reverse():
    io.output(motor_direction_pin_2, False)
    step_once()
    
    
def fw(arg, n_max, f) :  
    n=arg/(2*np.pi*f*Ts)               
    window = 0.5*(1-np.cos(2*np.pi*n/n_max)) #Hann window 
    out = np.cos(arg)*window  #Hann window ed cosine
    return out 

def generation_cos(f) :
    print("Frequency : ", f)
    A=pulses_per_rev/16 #Amplitude = Amax/coef
    N = 20 #number of period
    w=2*np.pi*f #pulsation 
    n_max= int(N/(f*Ts)) # maximum indice
    
    #initialization
    instructions = np.zeros(n_max)
    signal = np.zeros(n_max)
        
    for n in range (0, n_max):
        #step number between the nth Ts and nth-1 Ts
        nb_step = int(A*fw(w*n*Ts, n_max,f)-A*fw(w*(n-1)*Ts, n_max,f))  
        instructions[n] = nb_step
        signal[n] = A*fw(w*n*Ts, n_max,f)

        for i in range(0, abs(nb_step)):
            if nb_step>0 :
                step_forward()
            if nb_step<0 :
                step_reverse()
        time.sleep(Ts)
    print("Number of step between the begining and the end :", np.sum(instructions)) #caused by the discretizing

    
    fig=int(input("Figure ? (yes=1) : "))
    if fig==True :
        n=np.arange(0,n_max)
        s=np.zeros(len(n))
        for i in range(0,len(n)) :
            s[i] = np.sum(instructions[:i:])

        plt.figure()
        plt.plot(n, instructions, label="motor instructions")
        plt.plot(n, signal, "k--",label="theoretical signal")
        plt.plot(n, s, label="Rebuilt signal")
        plt.ylabel("number of step\n (1 tour = 1600)")
        plt.xlabel("n")
        plt.legend()
        plt.show()




#############################
# Motors immobilization
############################
# Setting the stepper pins to false so the motors will not move until the user presses the first key
io.output(motor_step_pin_1, False)
io.output(motor_step_pin_2, False)




##################
# User Interface
#################
nb=60
print("_"*nb)
print("{}Spring-coupled pendulum chain{}".format("#"*int((nb-27)/2),"#"*int((nb-27)/2)))
print("_"*nb)
print("Moteur 1 :")
print("a : step forward") #just one step/1600
print("z : step reverse") #just one step/1600
print("e : linear impulse") 
print("r : kink")
print("t : antikink")
print("\no : 5 kinks")
print("i : 5 antikinks")

print("_"*nb)
print("Moteur 2 :")
print("q : step forward")
print("s : step reverse")
print("d : linear impulse")
print("f : kink")
print("g : antikink")
print("\nh : Windowed sine of 20 periods (choosen frequency)")
print("k : 18 windowed sines of 20 periods (1.5 Hz to 10 Hz by step of 0.5Hz)")
print("l : 6 windowed sines of 20 periods (0.5 Hz to 3 Hz by step of 0.5Hz)")

print("_"*nb)
print("Moteurs 1 & moteur 2 :")
print("w : step forward")
print("x : step reverse")
print("c : kink & kink")
print("v : antikink & antikink")
print("b : kink & antikink")
print("n : antikink & kink")
print("_"*nb)
print("\nm : EXIT")
print("_"*nb)




################
#Infinite loop
################
# Infinite loop that will not end until the user presses the exit key ("m")

while True:
    # Keyboard character retrieval method is called and saved into variable
    char = getch()
    print(char)	

#Moteur 1
#########
    if (char == "a"): #one step
        step_forward_1()
        
    if (char == "z"): #one step
        step_reverse_1()
        
    if (char == "e") : #linear impulse
        for x in range(0, pulses_per_rev_lin):
            step_forward_1()
        for x in range(0, pulses_per_rev_lin):
            step_reverse_1()
    
    if (char == "r"): #kink
        for x in range(0, int((1+pulse_add)*pulses_per_rev)): #5 + 1/4
            step_forward_1()
        for x in range(0, int(pulse_add*pulses_per_rev)): # -1/4 (slowly comeback)
            step_reverse_1(delay2)
            
    if (char == "t"): #antikink
        for x in range(0, int((1+pulse_add)*pulses_per_rev)): #5 + 1/4
            step_reverse_1()
        for x in range(0, int(pulse_add*pulses_per_rev)): # -1/4 (slowly comeback)
            step_forward_1(delay2)
    
    
    if (char == "o"): #5 kinks
        for x in range(0, int(pulses_per_rev*5)): #5
            step_forward_1()
        for x in range(0, int(pulses_per_rev/4)): #+1/4
            step_forward_1()
        for x in range(0, int(pulses_per_rev/4)): #-1/4 (slowly)
            step_reverse_1(delay2)     
    
    if (char == "i"):
        for x in range(0, int(pulses_per_rev*5)): #5
            step_reverse_1()
        for x in range(0, int(pulses_per_rev/4)): #+1/4
            step_reverse_1()
        for x in range(0, int(pulses_per_rev/4)): #-1/4 (slowly)
            step_forward_1(delay2)  


#Motor 2
#########

    if (char == "q"): #one step
        step_forward_2()
        
    if (char == "s"): #one step
        step_reverse_2()
    
    if (char == "d"):  #linear impulse
        for x in range(0, pulses_per_rev_lin):
            step_forward_2()
        for x in range(0, pulses_per_rev_lin):
            step_reverse_2()

    if (char == "f"): #kink
        for x in range(0, int((1+pulse_add)*pulses_per_rev)):  #5 + 1/4
            step_forward_2()
        for x in range(0, int(pulse_add*pulses_per_rev)): # -1/4 (slowly comeback)
            step_reverse_2(delay2)
            
    if (char == "g"): #antikink
        for x in range(0, int((1+pulse_add)*pulses_per_rev)): #5 + 1/4
            step_reverse_2()
        for x in range(0, int(pulse_add*pulses_per_rev)): # -1/4 (slowly comeback)
            step_forward_2(delay2)
            

#Motors 1 and 2:
#######################

    if (char == "w"): #one step
        step_forward_both()

    if (char == "x"): #one step
        step_reverse_both()

    if (char == "c"): #kink - kink
        for x in range(0, int((1+pulse_add)*pulses_per_rev)): #5 + 1/4
            step_reverse_both()
        for x in range(0, int(pulse_add*pulses_per_rev)):  # -1/4 (slowly comeback)
            step_forward_both(delay2)
                
    if (char == "v"): #antikink - antikinik
        for x in range(0, int((1+pulse_add)*pulses_per_rev)): #5 + 1/4
            step_forward_both()
        for x in range(0, int(pulse_add*pulses_per_rev)):  # -1/4 (slowly comeback)
            step_reverse_both(delay2)

    if (char == "b"): #kink-antikink
        for x in range(0, int((1+pulse_add)*pulses_per_rev)): #5 + 1/4
            step_forward_1()
            step_reverse_2()
        for x in range(0, int(pulse_add*pulses_per_rev)) : # -1/4 (slowly comeback)
            step_reverse_1(delay2)
            step_forward_2(delay2)

    if (char == "n"): #antikink-kink
        for x in range(0, int((1+pulse_add)*pulses_per_rev)): #5 + 1/4
            step_forward_2()
            step_reverse_1()
        for x in range(0, int(pulse_add*pulses_per_rev)) : # -1/4 (slowly comeback)
            step_reverse_2(delay2)
            step_forward_1(delay2)
            
    if (char == "h"): 
        f=float(input("frequence :"))
        instructions=generation_cos(f)

    if (char == "k"): 
        for f in [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10] :
            instructions=generation_cos(f)
            time.sleep(1) #1s between wave packet
    
    if (char == "l"): 
        for f in [0.5, 1, 1.5, 2, 2.5, 3] :
            instructions=generation_cos(f)
            time.sleep(1) #1s between wave packet


#####
#Exit
#####
    # The "m" key will break the loop and exit the program
    if (char == "m"):
        print("Program Ended")
        break
    # The keyboard character variable will be set to blank, ready to save the next key that is pressed
    char = ""





