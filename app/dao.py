from bson import ObjectId
from pymongo import MongoClient
# from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.hlapi import *
import requests
from datetime import datetime, timedelta
import pytz

class dao:
    client=MongoClient('mongodb://localhost:27017')
    
    def __init__(self) -> None:
        self.db=dao.client["monitoring"]
        self.account=self.db["accounts"]
        self.clients=self.db["clients"]
        self.currentCity=""
        
    def getClients(self):
        objects:list=[]
        for obj in self.clients.find():
            objects.append(obj)
        return objects
    
    def addClient(self,object):
        self.clients.insert_one(object)
        
    def delete(self,id):
        id = ObjectId(id) if isinstance(id, str) else id
        self.clients.delete_one({"_id":id})
        
    def selectClient(self,id):
        id = ObjectId(id) if isinstance(id, str) else id
        client = self.clients.find_one({"_id":id})
        print(client)
        return self.clients.find_one({"_id":id})
    
    def update(self,object):
        self.clients.update_one({'_id':object['_id']},{'$set':object})
        
    def get_precipitation_history_openweather(self, city, start_date, end_date):
        BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
        API_KEY = "ad078127f38c94f851a179616e3eae8b"
        CITY = city
        self.currentCity=city
        
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        def kelvin_to_celsius(kelvin):
            celsius = kelvin - 273.15
            return celsius

        data_dict = {}

        while start_date <= end_date:
            timestamp = int(start_date.timestamp())
            url = f"{BASE_URL}appid={API_KEY}&q={CITY}&dt={timestamp}"
            response = requests.get(url).json()

            temp_kelvin = response['main']['temp']
            temp_celsius = kelvin_to_celsius(temp_kelvin)
            feels_like_kelvin = response['main']['feels_like']
            feels_like_celsius = kelvin_to_celsius(feels_like_kelvin)
            wind_speed = response['wind']['speed']
            humidity = response['main']['humidity']

            data_dict[start_date.strftime("%Y-%m-%d")] = {
                "Temperature": f"{temp_celsius:.2f}",
                "Feels Like": f"{feels_like_celsius:.2f}",
                "Humidity": f"{humidity}",
                "Wind Speed": f"{wind_speed}"
            }

            start_date += timedelta(days=1)
        return data_dict
        
    def Authentificate(self,login,password):
        result=self.account.find_one({'username':login,'password':password})
        if result != None:
            return True
        else :
            return False
    # def exist(self,object):
    #     results=self.clients.find_one({'_id':object['_id']})
    #     return results
    # def addUser(self,object):
    #     self.account.insert_one(object)
    def get(self, target, community,oid):
        ErrorIndication, ErrorStatus, ErrorIndex,varBinds= next(
            getCmd(SnmpEngine(),
                CommunityData(community),
                UdpTransportTarget((target, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
                )
        )
        if ErrorIndication :
            return f'Error Indication{ErrorIndication}'
        if ErrorStatus:
            return f'Error Status {ErrorStatus} ' 
        return varBinds[0]