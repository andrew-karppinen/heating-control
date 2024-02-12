import RPi.GPIO as GPIO 
from copy import deepcopy
import json
import time
from threading import Thread
from datetime import datetime,date,timedelta
import requests
import Adafruit_DHT as dht
import os

from src import *


GPIO.setwarnings(False) #disable warnings

        



class HeatingControl(Thread):

    def __init__(self,from_48_hour:bool = False,hour_count:int = 6,price_limit:float=5,thermal_limit:int=20):
        Thread.__init__(self)

        self.killed_ = False
        self.running_ = False
        self.ready_ = False #initialization complete (temperature measurement, picking up electricity prices).
        self.current_temp_ = 0

        self.is_chapest_hour_ = False

        self.hour_count_ = hour_count
        self.thermal_limit_ = thermal_limit
        self.max_temp_ = 0 #If this temperature is exceeded, heating is not kept on.
        self.temp_tracking_ = True
        
        self.error_in_internet_connection_ = True
        self.error_in_temp_read_ = True #Temperature measurement error until stated otherwise.
        self.from_48_hour_ = from_48_hour #Are we using a 12 or 42-hour time window for price comparison?


        self.heating_on_ = False
        self.current_price_ = 0
        self.price_limit_ = price_limit #If this electricity price drops, the heating is on continuously.

        self.timelimit_ = 7 #Checking if the temperature falls below the threshold, every 7 seconds.

        self.using_sql_ = False
        self.sql_object_ = None




    def Stop(self):
        self.running_ = False
        GPIO.cleanup() #clear gpio pins
        self.killed_ = True

    def WriteLogData(self):
        '''
        write events to csv file
        '''
        time = datetime.today().strftime('%Y-%m-%d %H:%M:%S') #get current time

        log_data_file = open("data/log data.csv","a")
        log_data_file.write(f"{time};{self.running_};{self.heating_on_};{self.current_price_};{self.temp_tracking_};{self.current_temp_};{self.thermal_limit_};{self.max_temp_};{self.from_48_hour_};{self.hour_count_}\n")
        log_data_file.close()





    def CreateSQLConnection(self,server_ip:str,username:str,password:str):
        self.sql_object_ = SQLConnection(server_ip,username,password)
        
    def UsingSQL(self,using:bool):
        self.using_sql_ = using
    
    def GetSettingsFromSQL(self):
        self.sql_object_.ReadSettingsFromSQL(self)



    def __IsChapestHour(self): #private method
        
        '''
        read 48h prices from json file


        :param cheapest_hours:
        :return: bool


        if the current price is among the lowest, return True

        '''
        
        
        hour = datetime.now().hour #get current hour

        today = str(date.today()) #current day
        yesterday = str(date.today() - timedelta(days=1)) #yesterday
        
        if os.path.isfile(f"data/prices/{today}.json") == True: #if today data is exist
            json_file_name = f"data/prices/{today}.json"
        elif os.path.isfile(f"data/prices/{yesterday}.json") == True: #if yesterday data is exist
            json_file_name = f"data/prices/{yesterday}.json"
        else:
            raise Exception("json file is not exist")


        with open(json_file_name) as json_file:
            json_data = json.load(json_file)

        #get current price:        
        self.current_price_ =  GetCurrentPrice(json_data) #get json


        if self.from_48_hour_ == True: #haetaan 48 tunnin hintatiedot

            prices = []
            for i in range(48):
                prices.append(json_data["prices"][i]["price"])
        else: #get 24-hour price data.
            prices = GetCurrentDayPrices(json_data)
        prices.sort()
        if self.current_price_ <= prices[self.hour_count_-1]: #if the current price is among the lowest
            self.is_chapest_hour_ = True
            return True
        else:
            self.is_chapest_hour_ = False

            return  False

    def TempTracking(self,on:bool): #turn temperature tracing on/off
        self.temp_tracking_ = on

    def SetThermalLimit(self,limit:int)->None:
        #Set new thermal limit
        self.thermal_limit_ = limit

    def SetMaxTemp(self,max_temp:int)->None:
        self.max_temp_ = max_temp

    def SetChapestHour(self,hour_count):
        self.hour_count_ = hour_count
    
    def SetPriceLimit(self,limit:int):
        self.price_limit_ = limit
    
    def TurnOnHeatingControl(self):
        #turn on automatic heating control
        self.running_ = True    
    
    def SetManuallyOn(self):
        #set manually
        if self.heating_on_ == False: #if heating is off, turn it on
            self.running_ = False
            RelayControl(True) 
            self.heating_on_ = True 
            self.WriteLogData() #save event to log data file

    
    def SetManuallyOff(self):
        if self.heating_on_ == True: #if heating is on, turn it off

            self.running_ = False
            RelayControl(False)
            self.heating_on_ = False
            self.WriteLogData() #save event to log data file



    def __SetHeatingOn(self):
        if self.temp_tracking_ == False or self.temp_tracking_ == True and self.current_temp_ < self.max_temp_:  #If heating tracking is enabled, ensure that the maximum temperature is not exceeded.
            if self.heating_on_ == False:  #if heating is on
                RelayControl(True)
                self.heating_on_ = True
                self.WriteLogData()  # save event to log data file

    def __SetHeatingOff(self):
        if self.heating_on_ == True:  #if heating is on
            RelayControl(False)  # set heating off
            self.heating_on_ = False
            self.WriteLogData()  # save event to log data file
    def run(self):

        self.current_temp_ = TempRead() #read temp
        if self.current_temp_ == None: #Error in temperature measurement
            self.temp_tracking_ = False
            self.error_in_temp_read_ = True
        else: #no error
            self.temp_tracking_ = True
            self.error_in_temp_read_ = False  
            
        
        if Write48hPricesToJSON() == False: #update prices and check internet connection
            self.error_in_internet_connection_ = True
        else: 
            self.error_in_internet_connection_ = False

        #init timers
        timer = time.time()


        self.ready_ = True
        while True: #main loop
            time.sleep(2) #delay
            
            if self.killed_ == True:
                exit() #kill python process





            if self.using_sql_ == True:
                self.sql_object_.ReadSettingsFromSQL(self) #read settings from sql database




            if self.running_ == True:  #if automaticly heating
                
                
                if Write48hPricesToJSON() == False: #update prices
                    self.error_in_internet_connection_ = True #Error getting prices.
                    self.__SetHeatingOn()

                    continue
                else: 
                    self.error_in_internet_connection_ = False
                    
                
                self.__IsChapestHour()
            

                if self.current_price_ < self.price_limit_: #price falls below the threshold.
                    self.__SetHeatingOn()



                #price not falls below the threshold.
                elif self.is_chapest_hour_ : #the current hour is among the cheapest.
                    self.__SetHeatingOn()

                else: #the current hour is not among the cheapest.
                    if self.temp_tracking_ == True and self.error_in_temp_read_ == False and self.current_temp_ <= self.thermal_limit_ : #current temperature falls below the threshold
                        self.__SetHeatingOn()

                    else:
                        self.__SetHeatingOff()


                if self.temp_tracking_ == True and self.error_in_temp_read_== False and time.time() - timer > self.timelimit_: #temperature
                    timer = time.time()
                    
                    self.current_temp_ = TempRead()
                    if self.current_temp_ == None: #Error in temperature measurement
                        self.temp_tracking_ = False
                        self.error_in_temp_read_ = True
                        continue


                    if self.current_temp_ < self.thermal_limit_: #current temperature falls below the threshold
                        self.__SetHeatingOn()

                        
                    elif self.__IsChapestHour() == False: #The current hour is not among the cheapest
                        self.__SetHeatingOff()








if __name__ == "__main__": #test program


    lammonohjaus = HeatingControl()
    lammonohjaus.running_ = True
    lammonohjaus.start()
    lammonohjaus.SetThermalLimit(25)
    i = 0
    while True:
        time.sleep(1)
        print(i)
        print(lammonohjaus.current_price_)
        print(lammonohjaus.current_temp_)
        print(lammonohjaus.heating_on_)
        print(lammonohjaus.IsChapestHour())
        i += 1