from bson import ObjectId
from pymongo import MongoClient
# from pysnmp.entity.rfc3413.oneliner import cmdgen
#from pysnmp.hlapi import *
import requests
from datetime import datetime, timedelta
import pytz

class Dao:
    client=MongoClient('mongodb://localhost:27017')
    #client=MongoClient('mongodb://db:36000')
    
    def __init__(self) -> None:
        self.db=Dao.client["monitoring"]
        self.account=self.db["accounts"]
        self.clients=self.db["Clients"]
        
        self.EndDevice=self.db["EndDevice"]
        self.City=self.db["City"]
        self.IOT=self.db["IOT"]
        
        self.currentCity=""
        
    def getClients(self):
        objects:list=[]
        for obj in self.clients.find():
            if obj["id"]!=0:
                objects.append(obj)
        return objects
    
    def getMaxId(self):
        object=self.clients.find().sort({ 'id': -1 }).limit(1)
        return object[0]['id']
    
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
    
    def updateClient(self,object):
        self.clients.update_one({'_id':object['_id']},{'$set':object})
        
    def Authentificate(self,login,password):
        result=self.account.find_one({'username':login,'password':password})
        if result != None:
            return True
        else :
            return False

    def addEndDevice(self, device):
        self.EndDevice.insert_one(device)
        
    def getEndDevices(self, id):
        objects:list=[]
        for obj in self.EndDevice.find({'id': id}):
            objects.append(obj)
        return objects
        
    def addCity(self, city):
        self.City.insert_one(city)
        
    def getCities(self, id):
        objects:list=[]
        for obj in self.City.find({'id': id}):
            objects.append(obj)
        return objects
        
    def addIOT(self, iot):
        self.IOT.insert_one(iot)
        
    def getIOTs(self, id):
        objects:list=[]
        for obj in self.IOT.find({'id': id}):
            objects.append(obj)
        return objects