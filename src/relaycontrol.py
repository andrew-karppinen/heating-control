import RPi.GPIO as GPIO
import time




def RelayControl(on:bool):


    gpio_pin = 27


    GPIO.setmode(GPIO.BCM)



    if on == True:
        GPIO.setup(gpio_pin, GPIO.OUT) #gpio pinni päälle

    elif on == False:

        GPIO.setup(gpio_pin,GPIO.IN) #gpio pinni pois päältä




if __name__ == "__main__":
    
    RelayControl(False)

  