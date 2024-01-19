from pysnmp.hlapi import *
import requests
from datetime import datetime, timedelta
import psutil

class Business:
    def __init__(self) -> None:
        pass
    def get_used_memory(self):
        try:
            memory_info = psutil.virtual_memory()

            used_memory_bytes = memory_info.used
            
            return used_memory_bytes
        except Exception as e:
            return None
            
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
        return int(str(varBinds[0]).split('=')[-1].strip())
    
    def walk(self, target, community, oid):
        results = []

        for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((target, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
            lexicographicMode=False, 
        ):
            if errorIndication:
                print(f"Error Indication: {errorIndication}")
                break
            elif errorStatus:
                print(f"Error Status: {errorStatus}")
                break
            else:
                for varBind in varBinds:
                    results.append(varBind[0])

        return results
    
    def get_disk_storage_info(self, target, community):
        storage = []
        usedStorage =[]
        # Iterate over storage table
        i=0
        for index in range(1, 10):  # Assuming a maximum of 10 partitions, adjust as needed
            try:
                hrStorageSize = int(self.get(target, community, f'1.3.6.1.2.1.25.2.3.1.5.{index}'))
                hrStorageUsed = int(self.get(target, community, f'1.3.6.1.2.1.25.2.3.1.6.{index}'))
            except:
                index = 11
                break

            hrStorageAllocationUnits = int(self.get(target, community, f'1.3.6.1.2.1.25.2.3.1.4.{index}'))
            hrStorageSize_gb = hrStorageSize * hrStorageAllocationUnits / (1024 ** 3)
            hrStorageUsed_gb = hrStorageUsed * hrStorageAllocationUnits / (1024 ** 3)
            
            storage.append(hrStorageSize_gb)
            usedStorage.append(hrStorageUsed_gb)
            i+=1
            
        storage.pop()
        storage.pop()
        usedStorage.pop()
        usedStorage.pop()
        
        ram_allocation_units = int(self.get(target, community, f'1.3.6.1.2.1.25.2.3.1.4.{i}'))
        ram = int(self.get(target, community, f'1.3.6.1.2.1.25.2.3.1.5.{i}'))
        ram_used = int(self.get(target, community, f'1.3.6.1.2.1.25.2.3.1.6.{i}'))
        
        ram_gb = ram * ram_allocation_units / (1024 ** 3)
        ram_used_gb = ram_used * ram_allocation_units / (1024 ** 3)

        return round(sum(storage), 2), round(sum(usedStorage), 2), round(ram_gb, 2), round(ram_used_gb, 2)

    def get_cpu_percentage(self, target, community):
        cpu_oid_base = '.1.3.6.1.2.1.25.3.3.1.2.'

        cpu_core_oids = self.walk(target, community, cpu_oid_base)

        core_values = []

        for core_oid in cpu_core_oids:
            core_values.append(self.get(target, community, core_oid))
            
            current_value = self.get(target, community, core_oid)
            #print(f"Core {core_oid}: Current Value - {current_value}")

        total_cpu_value = sum(core_values)
        percentage = total_cpu_value/len(core_values)

        return percentage

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