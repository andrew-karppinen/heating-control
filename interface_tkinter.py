from tkinter import *

from tkinter import IntVar, Frame
from tkinter import ttk
from src.heatingcontrol import *
from view_hours_tkinter import ViewHours
import json
window = Tk()

window.title("Lämmityksenohjaus") #nimetään ikkuna

window.geometry('640x480') #luodaan ikkuna

import os
import platform


def GetConfigDirectory():
    '''
    get this path in linux:
    home/.config/heating-control

    get this path in windows:
    appdata/Roaming
    '''

    system = platform.system()  # get operating system

    if system == "Linux":  # linux
        path = os.path.expanduser('~') + "/.config/heating-control"

        # Create the directory if it doesn't exist
        if not os.path.exists(path):
            os.makedirs(path)

        return path


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




    json_object = {'settings': {
        'thermal_limit': heatingcontrol.thermal_limit_,
        '48h':heatingcontrol.from_48_hour_,
        'hour_count': heatingcontrol.GetHourCount(),
        'mode':mode,
        'max_temperature': heatingcontrol.max_temp_,
        'price_limit': heatingcontrol.price_limit_,
        'temp_tracing': heatingcontrol.temp_tracking_

    }}

    json_object = json.dumps(json_object) #dict to json standard

    with open(f"{GetConfigDirectory()}/settings.json", "w") as outfile:
        outfile.write(json_object)






class GUI:
    def __init__(self): #constructor


        self.default_settings_ = {"settings": {"thermal_limit": 16, "48h": 0, "hour_count": 23, "mode": 1, "max_temperature": 0, "price_limit": 5, "temp_tracing": False}}

        #load settings
        try:
            f = open(f'{GetConfigDirectory()}/settings.json')
            self.settings_ = json.load(f)['settings']
            f.close()
        except: #settings file is no exist, create it and save default settings
            f = open(f'{GetConfigDirectory()}/settings.json','w')
            f.write(json.dumps(self.default_settings_))
            f.close()

            self.settings_ = self.default_settings_['settings']

        self.heatingcontrol_ = HeatingControl(self.settings_['48h'],self.settings_['hour_count'],self.settings_["price_limit"],self.settings_['thermal_limit']) #luodaan lämmityksenohjaus olio ja threadi
        self.heatingcontrol_.start() #käynnistetään lämmityksenohjaus threadi

        self.LoadingScreen()

        #määritellään joitain muuttujia:
        self.font_ = "Arial" #käytettävä fontti
        self.fontti_koko_ = 16 #fontin koko

        self.max_hintaraja_ = 50 #snt
        self.min_hintaraja_ = -20

        self.nappi_painettu_ = False


        #ikkunaan tulevat jutut:

        #Tuntimäärä
        tuntimaara_frame = Frame(window)
        tuntimaara_frame.pack(anchor=W, padx=10, pady=(20, 0))
        tuntimaara_label = Label(tuntimaara_frame, text="Tuntimäärä:              ",font=(self.font_, self.fontti_koko_)) #label
        tuntimaara_label.pack(side=LEFT)
        self.tuntimaara_ = IntVar(value=self.settings_["hour_count"])

        lisaa_tuntimaara = Button(tuntimaara_frame, text="         -      ",font=(self.font_, self.fontti_koko_)) #vähennä button
        lisaa_tuntimaara.pack(side=LEFT)
        self.tuntimaara_ilmaisin_label_ = Label(tuntimaara_frame, text=str(self.tuntimaara_.get()),font=(self.font_, self.fontti_koko_)) #tuntimäärä ilmaisn tekssti
        self.tuntimaara_ilmaisin_label_.pack(side=LEFT)
        vahenna_tuntimaara = Button(tuntimaara_frame, text="            +         ",font=(self.font_, self.fontti_koko_),command=self.LisaaTuntimaara) #kasvata button
        vahenna_tuntimaara.pack(side=LEFT)

        lisaa_tuntimaara.bind("<ButtonPress-1>", self.NappiPohjaan)
        lisaa_tuntimaara.bind("<ButtonRelease-1>", self.NappiYlos)

        #hintaraja
        hintaraja_frame  = Frame(window)
        hintaraja_frame .pack(anchor=W, padx=10, pady=(20, 0))
        hintaraja_label = Label(hintaraja_frame, text="Hintaraja:                  ",font=(self.font_, self.fontti_koko_)) #label
        hintaraja_label.pack(side=LEFT)
        self.hintaraja_ = IntVar(value=self.settings_["price_limit"])

        lisaa_hintaraja = Button(hintaraja_frame, text="         -        ",font=(self.font_, self.fontti_koko_),command=self.PienennaHintaRaja) #vähennä button
        lisaa_hintaraja.pack(side=LEFT)
        self.hintaraja_ilmaisin_label_ = Label(hintaraja_frame, text=str(self.hintaraja_.get()),font=(self.font_, self.fontti_koko_)) #hintaraja ilmaisn tekssti
        self.hintaraja_ilmaisin_label_.pack(side=LEFT)
        vahenna_hintaraja = Button(hintaraja_frame, text="          +         ",font=(self.font_, self.fontti_koko_),command=self.LisaaHintaRaja) #kasvata button
        vahenna_hintaraja.pack(side=LEFT)


        #maksimilämpötila
        max_lampotila_frame  = Frame(window)
        max_lampotila_frame .pack(anchor=W, padx=10, pady=(20, 0))
        max_lampotila_label = Label(max_lampotila_frame, text="Maksimilämpötila:    ",font=(self.font_, self.fontti_koko_)) #label
        max_lampotila_label.pack(side=LEFT)
        self.max_lampotila_  = IntVar(value=self.settings_["max_temperature"])

        lisaa_max_lampotila = Button(max_lampotila_frame, text="         -        ",font=(self.font_, self.fontti_koko_),command=self.PienennaMaxLampotila) #vähennä button
        lisaa_max_lampotila.pack(side=LEFT)
        self.max_lampotila_ilmaisin_label_ = Label(max_lampotila_frame, text=str(self.max_lampotila_.get()),font=(self.font_, self.fontti_koko_)) #hintaraja ilmaisn tekssti
        self.max_lampotila_ilmaisin_label_.pack(side=LEFT)
        vahenna_max_lampotila = Button(max_lampotila_frame, text="          +         ",font=(self.font_, self.fontti_koko_),command=self.LisaMaxLampotila) #kasvata button
        vahenna_max_lampotila.pack(side=LEFT)



        #minimi lämpötila
        lampotila_raja_frame  = Frame(window)
        lampotila_raja_frame .pack(anchor=W, padx=10, pady=(20, 0))
        min_lampotila_label = Label(lampotila_raja_frame, text="Minimilämpötila:       ",font=(self.font_, self.fontti_koko_)) #label
        min_lampotila_label.pack(side=LEFT)
        self.min_lampotila_  = IntVar(value=self.settings_["thermal_limit"])

        lisaa_lampotilarajaa = Button(lampotila_raja_frame, text="         -        ", font=(self.font_, self.fontti_koko_), command=self.PienennaLampotilarajaa) #vähennä button
        lisaa_lampotilarajaa.pack(side=LEFT)
        self.lampotilaraja_ilmaisin_label_ = Label(lampotila_raja_frame, text=str(self.min_lampotila_.get()), font=(self.font_, self.fontti_koko_)) #hintaraja ilmaisn tekssti
        self.lampotilaraja_ilmaisin_label_.pack(side=LEFT)
        vahenna_min_lampotila = Button(lampotila_raja_frame, text="        +         ", font=(self.font_, self.fontti_koko_), command=self.KasvataLampotilarajaa) #kasvata button
        vahenna_min_lampotila.pack(side=LEFT)




        #Frame radiobutton-elementeille
        checkbutton_frame = Frame(window)
        checkbutton_frame.pack()



        #ohjauksen radiobuttonit

        self.ohjaus_ = IntVar(value=self.settings_["mode"])

        ohjaus_frame = Frame(checkbutton_frame)
        ohjaus_frame.grid(row=6, column=1, columnspan=3)  # Yhdistetään kolme saraketta yhdeksi

        ohjaus_texts = ["Lämmitys pois", "Automaattinen ohjaus", "Lämmitys päälle"]
        ohjaus_values = [1, 2, 3]
        ohjaus_commands = [self.PaivitaOhjaus] * len(ohjaus_texts)

        style = ttk.Style()

        # Tyylien määrittely
        style.configure("TRadiobutton", font=(self.font_, self.fontti_koko_))
        style.map("TRadiobutton",
                  background=[('selected', 'lightblue'), ('!selected', 'white')],
                  foreground=[('selected', 'black'), ('!selected', 'gray')],
                  relief=[('selected', 'sunken'), ('!selected', 'raised')])

        for text, value, command in zip(ohjaus_texts, ohjaus_values, ohjaus_commands):
            r = ttk.Radiobutton(
                ohjaus_frame,
                text=text,
                variable=self.ohjaus_,
                value=value,
                command=command,
                style="TRadiobutton"
            )
            r.pack(side=LEFT, padx=5, pady=5)  # Aseta "padx" ja "pady" lisätäksesi tilaa

        # aikaikkuna-radiobuttonit

        self.aikaikkuna_ = IntVar(value=self.settings_["48h"]+1)





        self.lampotilan_seuranta_ = BooleanVar(value=self.settings_["temp_tracing"])



        if self.heatingcontrol_.error_in_temp_read_ == True:
            self.lampotilan_seuranta_.set(value=False)

        # Frame nappeja varten
        nappirivi_frame = Frame(checkbutton_frame)
        nappirivi_frame.grid(row=9, column=1, columnspan=3, sticky="w")


        buttons_padx = 30
        # Sulje, Tuntinäkymä ja Asetukset napit vierekkäin
        sulje = Button(nappirivi_frame, text="Sulje sovellus", command=self.Close, font=(self.font_, self.fontti_koko_))
        sulje.pack(side=LEFT, padx=buttons_padx, pady=0)

        tuntinakyma = Button(nappirivi_frame, text="Hintanäkymä", command=self.NaytaTuntinakyma,
                             font=(self.font_, self.fontti_koko_))
        tuntinakyma.pack(side=LEFT, padx=buttons_padx, pady=0)

        asetukset_btn = Button(nappirivi_frame, text="Asetukset", command=self.SettingsMenu,
                               font=(self.font_, self.fontti_koko_))
        asetukset_btn.pack(side=LEFT, padx=buttons_padx, pady=0)

        #teksti joka kertoo onko lämmitys päällä
        self.lammitys_paalla_ = StringVar()
        self.lammitys_paalla_.set("Lämmitys ei ole tällä hetkellä päällä!")
        
        Label(checkbutton_frame, textvariable=self.lammitys_paalla_,font=(self.font_, self.fontti_koko_)).grid(row =10,column=1,sticky="w")

    
        #teksti joka näyttää nykyisen sähkönhinnan
        self.hinta_nyt_ = StringVar()
        self.hinta_nyt_.set("Sähkön hinta nyt: 0.0 snt")
        
        Label(checkbutton_frame, textvariable=self.hinta_nyt_,font=(self.font_, self.fontti_koko_)).grid(row =11,column=1,sticky="w")


        #teksti joka kertoo onko sähkön hintatiedot haettu onnistuneesti
        self.hinnat_haettu_ = StringVar()
        self.hinnat_haettu_.set("Hintatiedot haettu onnistuneesti!",)
        
        Label(checkbutton_frame, textvariable=self.hinnat_haettu_,font=(self.font_, self.fontti_koko_)).grid(row =12,column=1,sticky="w")

        # Asetetaan oletusvalinnat
        self.PaivitaOhjaus()

        self.PaivitaAikaikkuna()

        self.PaivitaTekstit() #päivitetään tekstit



        window.protocol("WM_DELETE_WINDOW", self.Close) #close protocol

        window.mainloop() #start gui

    def SettingsMenu(self):
        settings_win = Toplevel(window)
        settings_win.title("Asetukset")
        settings_win.geometry("640x480")
        settings_win.transient(window)
        settings_win.grab_set()

        # Time-window radios
        aika_frame = Frame(settings_win)
        aika_frame.pack(anchor=W, padx=10, pady=(10, 5))
        aikaikkuna_texts = ["Käytä 23 tunnin aikaikkunaa", "Käytä 48 tunnin aikaikkunaa"]
        aikaikkuna_values = [1, 2]
        for text, value in zip(aikaikkuna_texts, aikaikkuna_values):
            r = ttk.Radiobutton(
                aika_frame,
                text=text,
                variable=self.aikaikkuna_,
                value=value,
                command=self.PaivitaAikaikkuna,
                style="TRadiobutton"
            )
            r.pack(side=LEFT, padx=5, pady=2)

        # Temperature tracking checkbox
        check_frame = Frame(settings_win)
        check_frame.pack(anchor=W, padx=10, pady=(5, 10))
        cb = ttk.Checkbutton(
            check_frame,
            text="Käytä lämpötilan seurantaa",
            variable=self.lampotilan_seuranta_,
            command=self.PaivitaLampotilanSeuranta,
            style="TCheckbutton"
        )
        cb.pack(anchor=W)

        # Close button
        close_btn = Button(settings_win, text="Sulje", command=settings_win.destroy,
                           font=(self.font_, self.fontti_koko_))
        close_btn.pack(pady=(5, 10))

    def Close(self):
        self.heatingcontrol_.Stop() #close heating control
        window.destroy() #close gui

    def LoadingScreen(self):

        while True:
            if self.heatingcontrol_.ready_ == True:
                return


    def NaytaTuntinakyma(self):
        hours = self.heatingcontrol_.Hours()
        if hours == False:#error in getting hours
            return

        ViewHours(hours)


    def PaivitaTekstit(self):
        '''
        Päivitetään info tekstit
        '''
        
        if self.heatingcontrol_.heating_on_ == True:
            self.lammitys_paalla_.set("Lämmitys on tällä hetkellä päällä!")
        else:
            self.lammitys_paalla_.set("Lämmitys ei ole tällä hetkellä päällä!")

        hinta = self.heatingcontrol_.current_price_ #hinta teksti
        self.hinta_nyt_.set(f"Sähkön hinta nyt: {hinta} snt")

        if self.heatingcontrol_.error_in_internet_connection_ == True:
            self.hinnat_haettu_.set("Ongelma hintojen haussa!")
        else:
            self.hinnat_haettu_.set("Hintatiedot haettu onnistuneesti!")



        window.after(1000, self.PaivitaTekstit) #päivitetään uudestaan sekunnin päästä



    def PaivitaLampotilanSeuranta(self):
        #päivitä lämpötilan seuranta päälle/pois päältä
        if self.heatingcontrol_.error_in_temp_read_ == True:
            self.lampotilan_seuranta_.set(value=False)
            return

        self.heatingcontrol_.TempTracking(self.lampotilan_seuranta_.get())

        SaveSettings(self.heatingcontrol_) #save settings to json file

    def PaivitaAikaikkuna(self):
        if self.aikaikkuna_.get() == 1: #23 tunnin aikaikkuna
            self.heatingcontrol_.from_48_hour_ = False
            if self.tuntimaara_.get() > 23: #jos tuntimäärä yli 23 aseta se 23
                self.tuntimaara_.set(23)

                self.heatingcontrol_.SetHourCount(self.tuntimaara_.get()) #päivitä lämmityksenohjaus 23 tuntiin
                SaveSettings(self.heatingcontrol_)  # save settings to json file

                self.tuntimaara_ilmaisin_label_.config(text=str(self.tuntimaara_.get()))  # Päivitä Label-widgetin teksti


        elif self.aikaikkuna_.get() == 2: #48 tunnin aikaikkuna
            self.heatingcontrol_.from_48_hour_ = True
        SaveSettings(self.heatingcontrol_) #save settings to json file

    def PaivitaOhjaus(self):
        if self.ohjaus_.get() == 1:
            self.heatingcontrol_.SetManuallyOff()
        elif self.ohjaus_.get() == 2:
            self.heatingcontrol_.TurnOnHeatingControl()
        elif self.ohjaus_.get() == 3:
            self.heatingcontrol_.SetManuallyOn()
        SaveSettings(self.heatingcontrol_) #save settings to json file


    def LisaaTuntimaara(self):
        '''
        Lisää tuntimäärää, päivittää tekstit käyttöliittymään,
        tekee muutokset lämityksenohajukseen,
        tallentaa asetukset json tiedostoon
        '''

        value = self.tuntimaara_.get()



        if self.heatingcontrol_.from_48_hour_ == False: #käytössä 23h
            if value >= 23: #tuntimäärä jo niin iso kuin mahdollista
                return  #ei tehdä mitään
        else: #käytössä 48h
            if value >= 47: #tuntimäärä jo niin iso kuin mahdollista
                return #ei tehdä mitään


        value += 1 #lisätään arvoa

        self.tuntimaara_.set(value)

        #tehään muutokset lämmitykseonhajukseen:
        self.heatingcontrol_.SetHourCount(value)
        SaveSettings(self.heatingcontrol_) #save settings to json file

        self.tuntimaara_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti



    def NappiPohjaan(self,event):
        self.nappi_painettu_ = True
        self.PienennaTuntimaara()


    def NappiYlos(self,event):
        self.nappi_painettu_ = False

    def PienennaTuntimaara(self):
        '''
        Vähentää tuntimäärää, päivittää tekstit käyttöliittymään,
        tekee muutokset lämityksenohajukseen,
        tallentaa asetukset json tiedostoon
        '''

        value = self.tuntimaara_.get()

        if value == 1: #jos jo niin pieni kuin mahdollista, ei tehdä mitään
            return

        value -= 1 #pienennetään arvoa

        self.tuntimaara_.set(value)

        #tehään muutokset lämmitykseonhajukseen:
        self.heatingcontrol_.SetHourCount(value)
        SaveSettings(self.heatingcontrol_) #save settings to json file

        self.tuntimaara_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti


        print(self.nappi_painettu_)
        if self.nappi_painettu_ == True:
            window.after(400, self.PienennaTuntimaara)  # automatically destroys the window in 10 seconds

    def LisaaHintaRaja(self):
        '''
        Lisää hintarajaa
        päivittää käyttöliittymän, tekee muutokset lämmityksenohajaukseen,
        tallentaa asetukset json tiedostoon
        '''

        value = self.hintaraja_.get()

        if value >= self.max_hintaraja_: #hintaraja on jo niin korkea kuin mahdollista
            return  #ei tehdä mitään

        value += 1
        self.hintaraja_.set(value)

        self.hintaraja_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti


        self.heatingcontrol_.SetPriceLimit(value)
        SaveSettings(self.heatingcontrol_)  # save settings to json file

        self.hintaraja_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti




    def PienennaHintaRaja(self):
        '''
        Pienentää hintarajaa
        päivittää käyttöliittymän, tekee muutokset lämmityksenohajaukseen,
        tallentaa asetukset json tiedostoon
        '''

        value = self.hintaraja_.get()

        if value <= self.min_hintaraja_:  # hintaraja on jo niin matala kuin mahdollista
            return  # ei tehdä mitään

        value -= 1
        self.hintaraja_.set(value)

        self.hintaraja_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti

        self.heatingcontrol_.SetPriceLimit(value)
        SaveSettings(self.heatingcontrol_)  # save settings to json file

        self.hintaraja_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti



    def LisaMaxLampotila(self):
        '''
        kasvattaa maksimilämpötilaa
        päivittää käyttöliittymän, tekee muutokset lämmityksenohajaukseen,
        tallentaa asetukset json tiedostoon
        '''

        value = self.max_lampotila_.get()

        if value >= 50: #jos maxlämpötila on jo niin suuri kuin mahdollista
            return #ei tehdä mitään

        value += 1
        self.max_lampotila_.set(value) #päivitetään käyttöliittymän maksimilämpötilamuuttuja

        self.heatingcontrol_.SetMaxTemp(value)
        SaveSettings(self.heatingcontrol_) #save settings to json file

        self.max_lampotila_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti


    def PienennaMaxLampotila(self):
        '''
        Pienentää maksimilämpötilaa
        päivittää käyttöliittymän, tekee muutokset lämmityksenohajaukseen,
        tallentaa asetukset json tiedostoon
        '''

        value = self.max_lampotila_.get()


        if value <=0:  # jos maxlämpötila on jo niin pieni kuin mahdollista
            return  # ei tehdä mitään

        value -= 1
        self.max_lampotila_.set(value) #päivitetään käyttöliittymän maksimilämpötilamuuttuja

        self.heatingcontrol_.SetMaxTemp(value)
        SaveSettings(self.heatingcontrol_)  # save settings to json file

        self.max_lampotila_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti


    def PienennaLampotilarajaa(self):
        '''
        Pienennetään lämpötilaraja
        päivittää käyttöliittymän, tekee muutokset lämmityksenohajaukseen,
        tallentaa asetukset json tiedostoon
        '''

        value = self.min_lampotila_.get()

        if value <= 0: #arvo jo niin pieni kuin mahdollista
            return  #ei tehdä mitään

        value -= 1
        self.min_lampotila_.set(value)
        self.heatingcontrol_.SetThermalLimit(value) #tehdään muutokset lämmityksenohjaukseen

        SaveSettings(self.heatingcontrol_)  # save settings to json file
        self.lampotilaraja_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti


    def KasvataLampotilarajaa(self):
        '''
        kasvatetaan lämpötilaraja
        päivittää käyttöliittymän, tekee muutokset lämmityksenohajaukseen,
        tallentaa asetukset json tiedostoon
        '''


        value = self.min_lampotila_.get()

        if value > 50: #arvo jo niin suuri kuin mahdollista
            return  #ei tehdä mitään

        value += 1
        self.min_lampotila_.set(value)
        self.heatingcontrol_.SetThermalLimit(value) #tehdään muutokset lämmityksenohjaukseen

        SaveSettings(self.heatingcontrol_)  # save settings to json file
        self.lampotilaraja_ilmaisin_label_.config(text=str(value))  # Päivitä Label-widgetin teksti



    def PaivitaLampotilaRaja(self, *args):
        value = self.lampotila_raja_.get()
        self.heatingcontrol_.SetThermalLimit(int(value))
        SaveSettings(self.heatingcontrol_) #save settings to json file




if __name__ == "__main__":
    GUI()