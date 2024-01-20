from dataclasses import dataclass,field
import datetime
from pymongo import MongoClient

@dataclass
class EndDevice():
    id:int
    date:datetime
    ram_used:float
    ram_total:float
    cpu_percentage:float
    storage_used:float
    storage_total:float

@dataclass
class IoTDevice():
    id:int
    temperature:float
    date:datetime
    
@dataclass
class CityWeather():
    id:int
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