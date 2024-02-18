from src.heatingcontrol import *
import json
import time
from threading import Thread

import PySimpleGUI as pg

from datetime import datetime


pg.theme("DarkAmber") #asetta tyylin





def SaveSettings(thermal_limit:int,max_temperature:int,price_limit:float,hour_count:int,time_frame_48h:bool,auto:bool,manually_on:bool,manually_off:bool,temp_tracing:bool):
    '''
    Save settings to json file
    file path: data/settings.json
    '''
    
    json_object = {'settings':{
        'thermal_limit':thermal_limit,
        '48h':time_frame_48h,
        'hour_count':hour_count,
        'auto':auto,
        'manually_on':manually_on,
        'manually_off':manually_off,
        'max_temperature':max_temperature,
        'price_limit':price_limit,
        'temp_tracing':temp_tracing
        
    }}
    
    json_object =  json.dumps(json_object)
    
    with open(f"data/settings.json", "w") as outfile:
        outfile.write(json_object)
        

def ViewHours(data):
    pg.theme('LightGrey1')  # Set the theme
    
    # Parse timestamp strings into datetime objects
    for item in data:
        item[0] = datetime.fromisoformat(item[0][:-1])
    
    # Sort data based on timestamp
    data.sort(key=lambda x: x[0])
    
    layout = []
    row = []
    row_count = 0
    
    current_datetime = datetime.now()
    current_hour = current_datetime.hour
    current_date = current_datetime.date()
    
    for item in data:
        timestamp = item[0]
        price = item[1]
        boolean_value = item[2]
        boolean_indicator = "True" if boolean_value else "False"
        
        # Determine the background color of the row
        timestamp_hour = timestamp.hour
        timestamp_date = timestamp.date()
        
        background_color = 'lightgreen' if timestamp_hour == current_hour and timestamp_date == current_date else 'lightgrey'
        
        row.append(pg.Text(f"Time: {timestamp}, Price: {price}, Boolean: {boolean_indicator}", background_color=background_color))
        
        row_count += 1
        
        # Split rows into multiple columns if they are too wide
        if row_count == 5:
            layout.append(row)
            row = []
            row_count = 0
    
    # Add any remaining rows
    if row:
        layout.append(row)

    layout.append([pg.Button("Close",key="close")]) #add close button

    window = pg.Window('Data Display Window', layout, resizable=True, finalize=True)
    
    while True:
        event, values = window.read()
        if event == pg.WINDOW_CLOSED:
            break

        elif event == "close":
            break

    window.close()


class ControlPanel:

    def __init__(self):


        f = open('data/settings.json')
        self.settings_ = json.load(f)['settings']
        f.close()
 
        


        self.heatingcontrol_ = HeatingControl(self.settings_['48h'],self.settings_['hour_count'],self.settings_["price_limit"],self.settings_['thermal_limit']) #luodaan lämmityksenohjaus olio ja threadi
        self.heatingcontrol_.start() #käynnistetään threadi

        self.LoadingScreen()


    def SQLsettings(self):
        layout = [
        [pg.Text("Palvelimen osoite:")],
        [pg.Input()],
        [pg.Text("Käyttäjä:")],
        [pg.Input()],
        [pg.Text("Salasana:")],
        [pg.Input()],
        [pg.Button("Testaa yhteyttä"),pg.Button("Tallenna"),pg.Button("Peruuta")]
        ]#ikkunaan tulevat jutut


        
        ikkuna = pg.Window("Lämmityksenohjaus",layout) #luo ikkunan
        
        lataus = 0 #muuttuja latausbaarin animointia varten
        while True:
            event,values = ikkuna.read() #päivitetään arvot vähintään joka 100 millisekuntti
            
            if event == "Peruuta" or event ==  pg.WIN_CLOSED: #jos ohjelma suljetaan
                ikkuna.close() #suljetaan ikkuna
                return
            
            
                
                

    def LoadingScreen(self):
        self.layout_ = [
        [pg.Text("Käynnistetään sovellusta")], 
        [pg.ProgressBar(20,key="latausruutu",size=(200,20))],#ikkunaan tulevat jutut
        [pg.Image("media/logo.png",size=(512,256))]
        ]

        
        self.screen_ = pg.Window("Lämmityksenohjaus", self.layout_, size=(700, 400)) #luo ikkunan
        
        lataus = 0 #muuttuja latausbaarin animointia varten
        while True:
            lataus+=1
            event,values = self.screen_.read(timeout=100) #päivitetään arvot vähintään joka 100 millisekuntti
            
            if event == "cancel" or event ==  pg.WIN_CLOSED: #jos ohjelma suljetaan
                self.screen_.close() #suljetaan ikkuna

                self.heatingcontrol_.Stop() #sulkee gpio pinnit 
            
            if lataus > 20:
                lataus = 0
            else:
                self.screen_["latausruutu"].update(lataus)
            
            
            
            if self.heatingcontrol_.ready_ == True:
                self.screen_.close()
                self.Main()
            
        
    def Main(self): #gui main function


        #read settings from json file

        #ikkkunaan tulevat jutut
        self.layout_ = [

            [pg.Text("Lämpötilaraja:",size=(30,1),font=('Arial Bold', 11), border_width=5)],
            [pg.Slider(range=(0, 30), default_value=self.settings_['thermal_limit'],
                        expand_x=True, enable_events=True,
                        orientation='horizontal', key='thermal_limit')],
            
            [pg.Text("Maksimilämpötila:",size=(30, 1), font=('Arial Bold', 11), border_width=5)],
            [pg.Slider(range=(10,40),default_value=self.settings_['max_temperature'],key='max_temp',expand_x=True, enable_events=True,
                       orientation='horizontal')],
            
            [pg.Text("Tuntimäärä:", size=(30, 1), font=('Arial Bold', 11), border_width=5)],
            [pg.Slider(range=(1, 47), default_value=self.settings_['hour_count'],
                       expand_x=True, enable_events=True,
                       orientation='horizontal', key='hour_count')],
            
            [pg.Text("Kytke lämmitys päälle jos sähkönhinta alle:", size=(40, 1), font=('Arial Bold', 11), border_width=5)],
            [pg.Slider(range=(0, 30), default_value=self.settings_["price_limit"],
                       expand_x=True, enable_events=True,
                       orientation='horizontal', key='min_price')],
            
            
            [pg.Text(f"",key="halvimpien_joukossa",size=(50, 1), font=('Arial Bold', 11))],
            [pg.Text(f"",key="hinta_nyt", size=(50, 1),font=('Arial Bold', 11))],
            [pg.Text(f"",key="lammitys_paalla",size=(50, 1), font=('Arial Bold', 11))],
            [pg.Text(f"",key="lampotila_nyt", size=(50, 1),font=('Arial Bold', 11))],
            [pg.Text(f"",key="virhe_yhteydessa", size=(50, 1),font=('Arial Bold', 11))],
            [pg.Radio('Lämmitys pois','settings',key='lammitys_pois', default=self.settings_['manually_off']),pg.Radio('Automaattinen ohjaus','settings',key ="automaattinen_ohjaus",default=self.settings_['auto']),pg.Radio("Lämmitys päälle",'settings',key="lammitys_paalle",default=self.settings_['manually_on'])],
            [pg.Checkbox('Käytä lämpötilan seurantaa',key='lampotilan_seuranta',default=self.settings_['temp_tracing'])],
            [pg.Radio("Käytä 23 tunnin aikaikkunaa","aikaikkuna",key="23tuntia",default=not self.settings_['48h']),pg.Radio("Käytä 48 tunnin aikaikkunaa","aikaikkuna",default=self.settings_['48h'],key="48tuntia")],
            [pg.Button("Käytä SQL yhteyttä",key="kaytasql")],
            [pg.Button("Käytä nykyisiä asetuksia oletuksena",key="tallenna")],
            [pg.Button("Näytä tunnit",key="view_hours")],
            [pg.Button("SQL asetukset")]
        ]


        self.screen_ = pg.Window("Lämmityksenohjaus", self.layout_, size=(700, 650)) #luo ikkunan



        while True:
            event,values = self.screen_.read(timeout=100) #päivitetään arvot vähintään joka 100 millisekuntti


            #luetaan asetukset heating_control --> interface            

            if event == "cancel" or event ==  pg.WIN_CLOSED: #jos ohjelma suljetaan
                self.screen_.close() #suljetaan ikkuna

                self.heatingcontrol_.Stop() #sulkee gpio pinnit 
                exit()
            

            
            elif event == "view_hours":
                hours =self.heatingcontrol_.Hours()
                ViewHours(hours)
            
            
            elif event == pg.TIMEOUT_EVENT: #ajoitetut päiviykset
                
                if self.heatingcontrol_.error_in_temp_read_ == False: #no error in temperature measurement
                    self.screen_['lampotilan_seuranta'].update(self.heatingcontrol_.temp_tracking_)
                    self.heatingcontrol_.TempTracking(values["lampotilan_seuranta"])
                    self.screen_["lampotila_nyt"].update(f"Nykyinen lämpötila: {self.heatingcontrol_.current_temp_}")

                else: #error in temperature measurement
                    self.screen_['lampotilan_seuranta'].update(False)
                    self.screen_["lampotila_nyt"].update("Virhe lämpötilan mittauksessa")
                
                if self.heatingcontrol_.error_in_internet_connection_ == True: #jos hintojen haussa ongelmia
                    self.screen_["virhe_yhteydessa"].update("Virhe hintojen haussa!")
                else: #ei ongelmia hintojen haussa
                    self.screen_["virhe_yhteydessa"].update("Hinnat haettu onnistuneesti!")
                    

                
                if self.heatingcontrol_.is_chapest_hour_:
                    self.screen_["halvimpien_joukossa"].update(f"Nykyinen tunti on halvimpien {values['hour_count']} tuntien joukossa!")
                else:
                    self.screen_["halvimpien_joukossa"].update(f"Nykyinen tunti ei ole halvimpien {values['hour_count']} tuntien joukossa!")
                if self.heatingcontrol_.heating_on_:
                    self.screen_["lammitys_paalla"].update(f"Lämmitys on tällä hetkellä päällä!")
                else:
                    self.screen_["lammitys_paalla"].update(f"Lämmitys ei ole tällä hetkellä päällä!")

                self.screen_["hinta_nyt"].update(f"Sähkönhinta nyt: {self.heatingcontrol_.current_price_} snt")





    

            #jos käyttäjä muuttaa jotain asetusta
            elif event == "hour_count":
                self.heatingcontrol_.SetChapestHour(int(values["hour_count"]))
            
            elif event == "thermal_limit":
                self.heatingcontrol_.SetThermalLimit(int(values["thermal_limit"]))
 
            elif event == "max_temp":
                self.heatingcontrol_.SetMaxTemp(int(values["max_temp"]))
            
            elif event == "min_price":
                self.heatingcontrol_.SetPriceLimit(values['min_price'])
            
            elif event == "tallenna":
                SaveSettings(int(values["thermal_limit"]),int(values["max_temp"]),values["min_price"],int(values["hour_count"]),values["48tuntia"],values["automaattinen_ohjaus"],values["lammitys_paalle"],values["lammitys_pois"],values["lampotilan_seuranta"])
                pg.popup("Tallennetut asetukset otetaan oletuksena käyttöön kun sovellus käynnistetään")
            
            
            elif event == "SQL asetukset":
                self.SQLsettings()
            elif event == "kaytasql":
                pass
                #self.heatingcontrol_.CreateSQLConnection("localhost","remote","BGnbjsuv0Opmk1")
                #self.heatingcontrol_.UsingSQL(True)
            
            
            
            #tarkistetaan radio buttonien tila
            if values['23tuntia'] == True: #24 tunnin aikaikkuna käytössä
                if values["hour_count"] > 23:
                    self.screen_["hour_count"].update(23)
                    self.heatingcontrol_.SetChapestHour(23)

                self.heatingcontrol_.from_48_hour_ = False

            elif values['48tuntia'] == True:
                self.heatingcontrol_.from_48_hour_ = True


            if  values['automaattinen_ohjaus'] == True:
                self.heatingcontrol_.TurnOnHeatingControl()
            elif values['lammitys_pois'] == True:
                self.heatingcontrol_.SetManuallyOff()
            elif values['lammitys_paalle'] == True:
                self.heatingcontrol_.SetManuallyOn()



        self.screen_.close()



if __name__ == "__main__":

    controlpanel = ControlPanel()


