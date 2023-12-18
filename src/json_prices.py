from datetime import datetime,date,timedelta
import requests
import os
import json




def Write48hPricesToJSON() -> bool:
    
    '''
    Hakee 42 tunin hintatiedot netistä ja kirjoittaa ne json tiedostoon
    
    Jos kello yli 16 ja tämän päivän hintatietoja ei ole haettu, haetaan uudet hintatiedot ja nimetään ne tänää päivän mukaan
    
    jos kello alle 16 ja tämän eikä eilisen päivän hintatietoja haettu haetaan uudet hintatiedot ja nimetään ne eilisen päivän mukaan
    
    tiedot tallennetaan json tiedostoon jotka nimetään päivien mukaan, tästä saadaan myös tieto minkä päivän hinnat on jo olemassa jne
    
    '''
    
    
    def Write(name_yesterday:bool) -> str:
        # write 48h prices to json file
        api_endpoint = f"https://api.porssisahko.net/v1/latest-prices.json"  # api endpoint
        json_data = requests.get(api_endpoint).json()  # get json

        json_object = json.dumps(json_data, indent=4)  # json to str
        
        if name_yesterday == False:
            with open(f"data/prices/{today}.json", "w") as outfile:
                outfile.write(json_object)
        else:
            with open(f"data/prices/{yesterday}.json", "w") as outfile:
                outfile.write(json_object)


    # get current date
    today = str(date.today())  # tämä päivä
    yesterday = str(date.today() - timedelta(days=1))  # eilinen päivä
    hour = datetime.now().hour  # nykyinen tunti

    if hour > 16:  # kello yli 16
        if os.path.isfile(f"data/prices/{today}.json") == False:  # if json file is not already in exist
            print("tässä")
            Write(name_yesterday=False)



    else:  # kello alle 16
        if os.path.isfile(f"data/prices/{yesterday}.json") == False:  # if json file is not already in exist
            if os.path.isfile(f"data/prices/{today}.json") == False:  # if json file is not already in exist

                Write(name_yesterday=True)


if __name__ == "__main__":
    Write48hPricesToJSON()