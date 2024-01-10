from dataclasses import dataclass,field
import datetime

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