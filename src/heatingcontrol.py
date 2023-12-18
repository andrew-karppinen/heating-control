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


        self.running_ = False
        self.ready_ = False #alkutoimet saatu tehtyä (lämpötilan mittaus, sähkönhintojen haku)
        self.current_temp_ = 0

        self.is_chapest_hour_ = False

        self.hour_count_ = hour_count
        self.thermal_limit_ = thermal_limit
        self.max_temp_ = 0 #jos tämä lämpötila ylittyy lämmitystä ei pideät päällä
        self.temp_tracking_ = True
        
        self.error_in_temp_read_ = True #lämötilan mittauksessa virhe kunnes toisin todetaan
        self.from_48_hour_ = from_48_hour #käytetäänkö 12 vai 42 tunnin aikaikkunaa hintojen vertailuun


        self.heating_on_ = False
        self.current_price_ = 0
        self.price_limit_ = price_limit #jos tämä sähkönhinta alittuu, lämmitys on kokoajan päällä

        self.timelimit_,timer = 3,0 #tarkistetaan onky nykyinen tunti halvimpien joukossa ja päivitetään hintatiedot
        self.timelimit2_,timer2 = 5,0 #temperature


    def Stop(self):
        self.running_ = False
        GPIO.cleanup() #clear gpio pins
        exit() #kill this thread

    def WriteLogData(self,on:bool,auto:bool):
        '''
        write events to csv file
        '''
        time = datetime.today().strftime('%Y-%m-%d %H:%M:%S') #get current time

        log_data_file = open("data/log data.csv","a")
        log_data_file.write(f"{time};{auto};{on};{self.current_price_};{self.current_temp_};{self.thermal_limit_};{self.from_48_hour_};{self.hour_count_};{self.thermal_limit_}\n")
        log_data_file.close()
        
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
        api_endpoint = f"https://api.porssisahko.net/v1/price.json?date={today}&hour={hour}" #api endpoint
        self.current_price_ =  requests.get(api_endpoint).json()['price'] #get json


        if self.from_48_hour_ == True: #haetaan 48 tunnin hintatiedot

            prices = []
            for i in range(48):
                prices.append(json_data["prices"][i]["price"])
        else: #haetaan 24 tunnin hintatiedot
            prices = GetCurrentDayPrices(json_data)
        prices.sort()
        if self.current_price_ <= prices[self.hour_count_]: #if the current price is among the lowest
            self.is_chapest_hour_ = True
            return True
        else:
            self.is_chapest_hour_ = False

            return  False

    def TempTracking(self,on:bool): #turn temperature tracing on/off
        self.temp_tracking_ = on

    def SetThermalLimit(self,limit:int)->None:
        #Asettaa uuden lämpötilarajan
        self.thermal_limit_ = limit

    def SetMaxTemp(self,max_temp:int)->None:
        self.max_temp_ = max_temp

    def SetChapestHour(self,hour_count):
        self.hour_count_ = hour_count
    
    def SetPriceLimit(self,limit:int):
        self.price_limit_ = limit
    
    def TurnOnHeatingControl(self):
        self.running_ = True    
    
    def SetManuallyOn(self):
        if self.heating_on_ == False: #jos lämmitys pois päältä, laitetaan se päälle
            self.running_ = False
            RelayControl(True) 
            self.heating_on_ = True 
            self.WriteLogData(True,False) #save event to log data file

    
    def SetManuallyOff(self):
        if self.heating_on_ == True: #jos lämmitys päällä, laitetaan se pois päältä

            self.running_ = False
            RelayControl(False)
            self.heating_on_ = False
            self.WriteLogData(False,False) #save event to log data file

    
    def run(self):

        self.current_temp_ = TempRead() #read temp
        if self.current_temp_ == None: #Error in temperature measurement
            self.temp_tracking_ = False
            self.error_in_temp_read_ = True
        else: #no error
            self.temp_tracking_ = True
            self.error_in_temp_read_ = False  
            
        
        Write48hPricesToJSON() #update prices


        #alustetaan ajastimet
        timer = time.time()
        timer2 = time.time()



        self.ready_ = True
        while True: #main loop

            if self.running_ == True:

                if self.current_price_ < self.price_limit_: #sähkönhinta alittaa rajan
                    if self.temp_tracking_ == False or self.temp_tracking_ == True and self.current_temp_ < self.max_temp_: #jos lämmityksen seuranta päällä, varmistetaan että maksimilämpötila ei ylity
                        if self.heating_on_ == False: #jos lämmitys pois päältä
                            RelayControl(True)
                            self.heating_on_ = True
                            self.WriteLogData(True,True) #save event to log data file  



                elif time.time() - timer > self.timelimit_: #sähkön hinta
                    timer = time.time()
                    Write48hPricesToJSON() #update prices
                    
                                        
                    
                    if self.__IsChapestHour(): #nykyinen tunti halvimpien joukossa
                        
                        if self.temp_tracking_ == False or self.self.temp_tracking_ == True and self.current_temp_ < self.max_temp_: #jos lämmityksen seuranta päällä, varmistetaan että maksimilämpötila ei ylity
                            if self.heating_on_ == False: #jos lämmitys pois päältä
                                RelayControl(True)
                                self.heating_on_ = True
                                self.WriteLogData(True,True) #save event to log data file


                    else: #jos nykyinen tunti ei ole halvimpien joukossa
                        if self.temp_tracking_ == True and self.error_in_temp_read_ == False and self.current_temp_ <= self.thermal_limit_ : #lämpötila alittaa rajan
                            if self.heating_on_ == False: #jos lämmitys pois päältä
                                RelayControl(True) #set heating on
                                self.heating_on_ = True
                                self.WriteLogData(True,True) #save event to log data file
                        else:
                            if self.heating_on_ == True: #jos lämmitys päällä 
                                RelayControl(False) #set heating off
                                self.heating_on_ = False
                                self.WriteLogData(False,True) #save event to log data file



                if self.temp_tracking_ == True and self.error_in_temp_read_== False and time.time() - timer2 > self.timelimit2_: #lämpötila
                    timer2 = time.time()
                    
                    self.current_temp_ = TempRead()
                    if self.current_temp_ == None: #Error in temperature measurement
                        self.temp_tracking_ = False
                        self.error_in_temp_read_ = True
                        
                        continue


                    if self.current_temp_ < self.thermal_limit_: #nykyinen lämpötila alittaa rajan
                        if self.heating_on_ == False: #jos lämmitys pois päältä

                            RelayControl(True)
                            self.heating_on_ = True
                            self.WriteLogData(True,True) #save event to log data file

                        
                    elif self.__IsChapestHour() == False: #nykyinen tunti ei halvimpien joukssa
                        if self.heating_on_ == True: #jos lämmitys päällä 
                            RelayControl(False) #set heating off
                            self.heating_on_ = False #set heating off
                            self.WriteLogData(False,True) #save event to log data file



            time.sleep(0.5) #delay





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