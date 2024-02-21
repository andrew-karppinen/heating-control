








def TempRead()->float:

    DHT = 4
    # Read Temp and Hum from DHT22 or DHT11
    #if error return None


    try:
        import Adafruit_DHT as dht #try import dht library
    except:
        return None #error with import dht


    try: #try dht22

        h, t = dht.read_retry(dht.DHT22, DHT)
    except:
        try: #try dht11
           h, t = dht.read_retry(dht.DHT11, DHT) 
        except:
            return None #error with dht22 and dht11
        else:
            retrun(t) #no error with dht11
        
    else: #no error with dht22
        return(t)



if __name__ == "__main__":

    print(TempRead())