from dataclasses import dataclass,field
import datetime
from pymongo import MongoClient

@dataclass
class EndDevice():
    id:int
    name:str
    address:str
    longitude:float
    latitude:float
    memory_usage:float
    cpu_usage:float
    disk_usage:float

@dataclass
class IoTDevice():
    id:int
    name:str
    adress:str
    longitude:float
    latitude:float
    temperature:float
    
@dataclass
class CityWeather():
    id:int
    name:str
    adress:str
    longitude:float
    latitude:float
    precipitation:float
    date:datetime
    
@dataclass
class Device:
    ip:str
    description:str
    
@dataclass
class Iot:
    mac:str
    temp:float
    
class IotDao:
    @staticmethod
    def getAll():
        client=MongoClient('mongodb://localhost:36000')
        db=client["db_hosts"]
        #db["test"].insert_one({"id":1})
        objects:list=[]
        for obj in db["test"].find():
            objects.append(obj)
        print(objects)
if __name__ == "__main__":
    IotDao.getAll()