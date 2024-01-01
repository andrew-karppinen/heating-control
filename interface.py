from src.heatingcontrol import *
import json
import time
from threading import Thread

import PySimpleGUI as pg



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
        



class ControlPanel:

    def __init__(self):


        f = open('data/settings.json')
        self.settings_ = json.load(f)['settings']
        f.close()
 
        


        self.heatingcontrol_ = HeatingControl(self.settings_['48h'],self.settings_['hour_count'],self.settings_["price_limit"],self.settings_['thermal_limit']) #luodaan lämmityksenohjaus olio ja threadi
        self.heatingcontrol_.start() #käynnistetään threadi

        self.LoadingScreen()


    def LoadingScreen(self):
        self.layout_ = [
        [pg.Text("Käynnistetään sovellusta")], 
        [pg.ProgressBar(20,key="latausruutu",size=(200,20))],#ikkunaan tulevat jutut
        [pg.Image("media/logo.png",size=(512,256))]
        ]

        
        self.ikkuna_ = pg.Window("Lämmityksenohjaus",self.layout_,size=(700,400)) #luo ikkunan
        
        lataus = 0 #muuttuja latausbaarin animointia varten
        while True:
            lataus+=1
            event,values = self.ikkuna_.read(timeout=100) #päivitetään arvot vähintään joka 100 millisekuntti
            
            if event == "cancel" or event ==  pg.WIN_CLOSED: #jos ohjelma suljetaan
                self.ikkuna_.close() #suljetaan ikkuna

                self.heatingcontrol_.Stop() #sulkee gpio pinnit 
            
            if lataus > 20:
                lataus = 0
            else:
                self.ikkuna_["latausruutu"].update(lataus)
            
            
            
            if self.heatingcontrol_.ready_ == True:
                self.ikkuna_.close()
                self.Main()
            
        
    def Main(self): #gui main function


        #read settings from json file

        #ikkkunaan tulevat jutut
        self.layout_ = [

            [pg.Text("Lämpötilaraja:",size=(30,1),font=('Arial Bold', 11), border_width=5)],
            [pg.Slider(range=(0, 30), default_value=self.settings_['thermal_limit'],
                        expand_x=True, enable_events=True,
                        orientation='horizontal', key='lampotilaraja')],
            
            [pg.Text("Maksimilämpötila:",size=(30, 1), font=('Arial Bold', 11), border_width=5)],
            [pg.Slider(range=(10,40),default_value=self.settings_['max_temperature'],key='max_lampotila',expand_x=True, enable_events=True,
                       orientation='horizontal')],
            
            [pg.Text("Tuntimäärä:", size=(30, 1), font=('Arial Bold', 11), border_width=5)],
            [pg.Slider(range=(1, 47), default_value=self.settings_['hour_count'],
                       expand_x=True, enable_events=True,
                       orientation='horizontal', key='tuntimaara')],
            
            [pg.Text("Kytke lämmitys päälle jos sähkönhinta alle:", size=(40, 1), font=('Arial Bold', 11), border_width=5)],
            [pg.Slider(range=(0, 30), default_value=self.settings_["price_limit"],
                       expand_x=True, enable_events=True,
                       orientation='horizontal', key='min_hinta')],
            
            
            [pg.Text(f"",key="halvimpien_joukossa",size=(50, 1), font=('Arial Bold', 11))],
            [pg.Text(f"",key="hinta_nyt", size=(50, 1),font=('Arial Bold', 11))],
            [pg.Text(f"",key="lammitys_paalla",size=(50, 1), font=('Arial Bold', 11))],
            [pg.Text(f"",key="lampotila_nyt", size=(50, 1),font=('Arial Bold', 11))],
            [pg.Text(f"",key="virhe_yhteydessa", size=(50, 1),font=('Arial Bold', 11))],
            [pg.Radio('Lämmitys pois','settings',key='lammitys_pois', default=self.settings_['manually_off']),pg.Radio('Automaattinen ohjaus','settings',key ="automaattinen_ohjaus",default=self.settings_['auto']),pg.Radio("Lämmitys päälle",'settings',key="lammitys_paalle",default=self.settings_['manually_on'])],
            [pg.Checkbox('Käytä lämpötilan seurantaa',key='lampotilan_seuranta',default=self.settings_['temp_tracing'])],
            [pg.Radio("Käytä 23 tunnin aikaikkunaa","aikaikkuna",key="23tuntia",default=not self.settings_['48h']),pg.Radio("Käytä 48 tunnin aikaikkunaa","aikaikkuna",default=self.settings_['48h'],key="48tuntia")],
            [pg.Button("Käytä nykyisiä asetuksia oletuksena",key="tallenna")]
        ]


        self.ikkuna_ = pg.Window("Lämmityksenohjaus",self.layout_,size=(700,650)) #luo ikkunan



        while True:
            event,values = self.ikkuna_.read(timeout=100) #päivitetään arvot vähintään joka 100 millisekuntti


            if event == "cancel" or event ==  pg.WIN_CLOSED: #jos ohjelma suljetaan
                self.ikkuna_.close() #suljetaan ikkuna

                self.heatingcontrol_.Stop() #sulkee gpio pinnit 


            elif event == pg.TIMEOUT_EVENT: #ajoitetut päiviykset
                
                if self.heatingcontrol_.error_in_temp_read_ == False: #no error in temperature measurement
                    self.ikkuna_['lampotilan_seuranta'].update(self.heatingcontrol_.temp_tracking_)
                    self.heatingcontrol_.TempTracking(values["lampotilan_seuranta"])
                    self.ikkuna_["lampotila_nyt"].update(f"Nykyinen lämpötila: {self.heatingcontrol_.current_temp_}")

                else: #error in temperature measurement
                    self.ikkuna_['lampotilan_seuranta'].update(False)
                    self.ikkuna_["lampotila_nyt"].update("Virhe lämpötilan mittauksessa")
                
                if self.heatingcontrol_.error_in_internet_connection_ == True: #jos hintojen haussa ongelmia
                    self.ikkuna_["virhe_yhteydessa"].update("Virhe hintojen haussa!")
                else: #ei ongelmia hintojen haussa
                    self.ikkuna_["virhe_yhteydessa"].update("Hinnat haettu onnistuneesti!")
                    

                
                if self.heatingcontrol_.is_chapest_hour_:
                    self.ikkuna_["halvimpien_joukossa"].update(f"Nykyinen tunti on halvimpien {values['tuntimaara']} tuntien joukossa!")
                else:
                    self.ikkuna_["halvimpien_joukossa"].update(f"Nykyinen tunti ei ole halvimpien {values['tuntimaara']} tuntien joukossa!")
                if self.heatingcontrol_.heating_on_:
                    self.ikkuna_["lammitys_paalla"].update(f"Lämmitys on tällä hetkellä päällä!")
                else:
                    self.ikkuna_["lammitys_paalla"].update(f"Lämmitys ei ole tällä hetkellä päällä!")

                self.ikkuna_["hinta_nyt"].update(f"Sähkönhinta nyt: {self.heatingcontrol_.current_price_} snt")
                
    

            #jos käyttäjä muuttaa jotain asetusta
            elif event == "tuntimaara":
                self.heatingcontrol_.SetChapestHour(int(values["tuntimaara"]))
            
            elif event == "lampotilaraja":
                self.heatingcontrol_.SetThermalLimit(int(values["lampotilaraja"]))
 
            elif event == "max_lampotila":
                self.heatingcontrol_.SetMaxTemp(int(values["max_lampotila"]))
            
            elif event == "min_hinta":
                self.heatingcontrol_.SetPriceLimit(values['min_hinta'])
            
            elif event == "tallenna":
                SaveSettings(int(values["lampotilaraja"]),int(values["max_lampotila"]),values["min_hinta"],int(values["tuntimaara"]),values["48tuntia"],values["automaattinen_ohjaus"],values["lammitys_paalle"],values["lammitys_pois"],values["lampotilan_seuranta"])
                pg.popup("Tallennetut asetukset otetaan oletuksena käyttöön kun sovellus käynnistetään")
            
            #tarkistetaan radio buttonien tila
            if values['23tuntia'] == True: #24 tunnin aikaikkuna käytössä
                if values["tuntimaara"] > 23:
                    self.ikkuna_["tuntimaara"].update(23)
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



        self.ikkuna_.close()



if __name__ == "__main__":

    controlpanel = ControlPanel()


