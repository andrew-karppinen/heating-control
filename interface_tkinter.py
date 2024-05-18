from tkinter import *

from src.heatingcontrol import *
from view_hours_tkinter import ViewHours

window = Tk()

window.title("Lämmityksenohjaus") #nimetään ikkuna

window.geometry('700x500') #luodaan ikkuna


def SaveSettings(heatingcontrol:object):
    '''
    Save settings to json file
    file path: data/settings.json
    '''

    if heatingcontrol.running_==False and heatingcontrol.heating_on_==False:
        mode = 1
    elif heatingcontrol.running_==False and heatingcontrol.heating_on_==True:
        mode = 3
    elif heatingcontrol.running_==True:
        mode = 2
        
    #mode1 = off, mode2 = auto, mode3 = on
    

    if heatingcontrol.from_48_hour_==True:
        time_window = 2
    else:
        time_window = 1


    json_object = {'settings': {
        'thermal_limit': heatingcontrol.thermal_limit_,
        '48h':time_window,
        'hour_count': heatingcontrol.hour_count_,
        'mode':mode,
        'max_temperature': heatingcontrol.max_temp_,
        'price_limit': heatingcontrol.price_limit_,
        'temp_tracing': heatingcontrol.temp_tracking_

    }}

    json_object = json.dumps(json_object) #dict to json standard

    with open(f"data/settings.json", "w") as outfile:
        outfile.write(json_object)

class GUI:
    def __init__(self): #constructor


        #load settings
        f = open('data/settings.json')
        self.settings_ = json.load(f)['settings']
        f.close()


        self.heatingcontrol_ = HeatingControl(self.settings_['48h'],self.settings_['hour_count'],self.settings_["price_limit"],self.settings_['thermal_limit']) #luodaan lämmityksenohjaus olio ja threadi
        self.heatingcontrol_.start() #käynnistetään lämmityksenohjaus threadi

        self.LoadingScreen()




        #tuntimaara:
        self.tuntimaara_ = IntVar(value=self.settings_["hour_count"])
        self.tuntimaara_.trace("w", self.PaivitaTuntimaara)  # Lisää jäljitys, joka kutsuu on_slider_change-metodia aina kun arvo muuttuu
        Scale(window, variable=self.tuntimaara_, from_=1, to=47, orient=HORIZONTAL, length=300,label="Tuntimäärä: ").pack(anchor=CENTER)# Keskitä liukusäädin vaakasuunnassa




        #hintaraja:
        self.hintaraja_ = IntVar(value=self.settings_["price_limit"])
        self.hintaraja_.trace("w", self.PaivitaHintaRaja)  # Lisää jäljitys, joka kutsuu on_slider_change-metodia aina kun arvo muuttuu
        Scale(window, variable=self.hintaraja_ , from_=0, to=50, orient=HORIZONTAL, length=300,label="Kytke lämmitys päälle jos hinta alle (snt): ").pack(anchor=CENTER)# Keskitä liukusäädin vaakasuunnassa

        #maksimi lämpötila
        self.max_lampotila_ = IntVar(value=self.settings_["max_temperature"])
        self.max_lampotila_.trace("w", self.PaivitaMaxLampotila)  # Lisää jäljitys, joka kutsuu on_slider_change-metodia aina kun arvo muuttuu
        self.s3 = Scale(window, variable=self.max_lampotila_ , from_=0, to=40, orient=HORIZONTAL, length=300,label="Älä käytä lämmitystä jos lämpötila yli: ").pack(anchor=CENTER)# Keskitä liukusäädin vaakasuunnassa

        #minimilämpötila
        self.lampotila_raja_ = IntVar(value=self.settings_["thermal_limit"])
        self.lampotila_raja_.trace("w", self.PaivitaLampotilaRaja)  # Lisää jäljitys, joka kutsuu on_slider_change-metodia aina kun arvo muuttuu
        Scale(window, variable=self.lampotila_raja_, from_=0, to=40, orient=HORIZONTAL, length=300, label="Kytke lämmitys päälle jos lämpötila alle: ").pack(anchor=CENTER)# Keskitä liukusäädin vaakasuunnassa



        # Frame radiobutton-elementeille
        checkbutton_frame = Frame(window)
        checkbutton_frame.pack()




        self.ohjaus_ = IntVar(value=self.settings_["mode"])

        r1 = Radiobutton(checkbutton_frame, text="Lämmitys pois", variable=self.ohjaus_, value=1, command=self.PaivitaOhjaus)

        r2 = Radiobutton(checkbutton_frame, text="Automaattinen ohjaus", variable=self.ohjaus_, value=2, command=self.PaivitaOhjaus)

        r3 = Radiobutton(checkbutton_frame, text="Lämmitys päälle", variable=self.ohjaus_, value=3, command=self.PaivitaOhjaus)

        r1.grid(row=6, column=1)
        r2.grid(row=6, column=2)
        r3.grid(row=6, column=3)


        self.aikaikkuna_ = IntVar(value=self.settings_["48h"])



        r4 = Radiobutton(checkbutton_frame, text="Käytä 12 tunnin aikaikkunaa", variable=self.aikaikkuna_, value=1, command=self.PaivitaAikaikkuna)

        r5 = Radiobutton(checkbutton_frame, text="Käytä 48 tunnin aikaikkunaa", variable=self.aikaikkuna_, value=2, command=self.PaivitaAikaikkuna)

        r4.grid(row=7, column=1)
        r5.grid(row=7, column=2)


        self.lampotilan_seuranta_ = BooleanVar(value=self.settings_["temp_tracing"])


        self.checkbutton_lampotilan_seuranta_ = Checkbutton(checkbutton_frame, text="Käytä lämpötilan seurantaa", variable=self.lampotilan_seuranta_, command=self.PaivitaLampotilanSeuranta)
        self.checkbutton_lampotilan_seuranta_.grid(row=8, column=1)


        if self.heatingcontrol_.error_in_temp_read_ == True:
            self.lampotilan_seuranta_.set(value=False)


        sulje = Button(checkbutton_frame,text="Sulje ohjelma",command=self.Close)
        sulje.grid(row =9,column=1)

        tuntinakyma = Button(checkbutton_frame,text="Tuntinäkymä",command=self.NaytaTuntinakyma)
        tuntinakyma.grid(row =9,column=2)

        # Asetetaan oletusvalinnat
        self.PaivitaOhjaus()

        self.PaivitaAikaikkuna()




        window.protocol("WM_DELETE_WINDOW", self.Close) #close protocol

        window.mainloop() #start gui

    def Close(self):
        self.heatingcontrol_.Stop() #close heating control
        window.destroy() #close gui

    def LoadingScreen(self):

        while True:
            if self.heatingcontrol_.ready_ == True:
                return


    def NaytaTuntinakyma(self):
        hours = self.heatingcontrol_.Hours()
        ViewHours(hours)


    def PaivitaLampotilanSeuranta(self):
        #päivitä lämpötilan seuranta päälle/pois päältä

        if self.heatingcontrol_.error_in_temp_read_ == True:
            self.lampotilan_seuranta_.set(value=False)
            return

        self.heatingcontrol_.TempTracking(self.lampotilan_seuranta_.get())

        SaveSettings(self.heatingcontrol_) #save settings to json file

    def PaivitaAikaikkuna(self):
        if self.aikaikkuna_.get() == 1:
            self.heatingcontrol_.from_48_hour_ = False
            if self.tuntimaara_.get() > 23: #jos tuntimäärä yli 23 aseta se 23
                self.tuntimaara_.set(23)
                value = 23
            
            
        elif self.aikaikkuna_.get() == 2:
            self.heatingcontrol_.from_48_hour_ = True
        SaveSettings(self.heatingcontrol_) #save settings to json file

    def PaivitaOhjaus(self):
        print(self.ohjaus_.get())
        if self.ohjaus_.get() == 1:
            self.heatingcontrol_.SetManuallyOff()
        elif self.ohjaus_.get() == 2:
            self.heatingcontrol_.TurnOnHeatingControl()
        elif self.ohjaus_.get() == 3:
            self.heatingcontrol_.SetManuallyOn()
        SaveSettings(self.heatingcontrol_) #save settings to json file

    def PaivitaTuntimaara(self, *args):
        value = self.tuntimaara_.get()

        if self.heatingcontrol_.from_48_hour_ == False:
            if value > 23:
                self.tuntimaara_.set(23)
                value = 23

        self.heatingcontrol_.SetChapestHour(value)
        SaveSettings(self.heatingcontrol_) #save settings to json file

    def PaivitaHintaRaja(self, *args):
        value = self.hintaraja_.get()
        self.heatingcontrol_.SetPriceLimit(value)
        SaveSettings(self.heatingcontrol_) #save settings to json file

    def PaivitaMaxLampotila(self, *args):
        value = self.max_lampotila_.get()
        self.heatingcontrol_.SetMaxTemp(value)
        SaveSettings(self.heatingcontrol_) #save settings to json file


    def PaivitaLampotilaRaja(self, *args):
        value = self.lampotila_raja_.get()
        self.heatingcontrol_.SetThermalLimit(int(value))
        SaveSettings(self.heatingcontrol_) #save settings to json file




if __name__ == "__main__":
    GUI()