from bson import ObjectId
from pymongo import MongoClient
# from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.hlapi import *
import requests
from datetime import datetime, timedelta
import pytz

class dao:
    client=MongoClient('mongodb://localhost:27017')
    #client=MongoClient('mongodb://db:36000')
    
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
    