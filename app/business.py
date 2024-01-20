from pysnmp.hlapi import *
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from sklearn.linear_model import LinearRegression

class Business:
    def __init__(self) -> None:
        self.cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        self.retry_session = retry(self.cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)
            
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
        i=0
        for index in range(1, 10):
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
    
    def get_precipitation_history(self, latitude, longitude, start_date, end_date):
        #print(f"lat : {latitude}, log : {longitude}, start_date : {start_date}, end_date : {end_date}")
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": "temperature_2m",
                "start": start_date,
                "end": end_date
            }
            responses = self.openmeteo.weather_api(url, params=params)

            response = responses[0]
            # Check if the response contains the expected data
            if hasattr(response, 'Hourly') and response.Hourly() and response.Hourly().Variables(0):
                hourly = response.Hourly()
                precipitation_data = hourly.Variables(0).ValuesAsNumpy()

                return precipitation_data
            else:
                print("Unexpected response format. Unable to retrieve precipitation data.")
                return None
        except Exception as e:
            print(f"Caught an exception: {e}")
    
    def predict_precipitation(self, X, y):
        model = LinearRegression()
        model.fit(X, y)
        return model.predict(X)
    
    def get_coordinates(self, city_name):
        geolocator = Nominatim(user_agent="your_app_name")
        location = geolocator.geocode(city_name)
        return (location.latitude, location.longitude)
    
    def plot_precipitation(self, city, start_date, end_date, save_path=None):
        latitude, longitude = self.get_coordinates(city)
        precipitation_history = self.get_precipitation_history(latitude, longitude, start_date, end_date)
        #print(f"presip : {precipitation_history}")
        
        plt.figure(figsize=(10, 5))
        plt.plot(start_date + pd.to_timedelta(range(len(precipitation_history)), unit='h'), precipitation_history, label='Precipitation History')
        plt.xlabel('Date')
        plt.ylabel('Precipitation')
        plt.title(f'Precipitation History for {city}')
        plt.legend()

        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

        plt.close()

        if save_path:
            return save_path
        else:
            return None

    def plot_predictions(self, X, y, save_path=None):
        predictions = self.predict_precipitation(X, y)

        plt.figure(figsize=(10, 5))
        plt.plot(range(len(predictions)), predictions, label='Predictions')
        plt.xlabel('Time')
        plt.ylabel('Predicted Precipitation')
        plt.title('Predictions')
        plt.legend()

        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

        plt.close()

        if save_path:
            return save_path
        else:
            return None

    def create_dashboard_city(self, city, start_date, end_date):
        start_date = datetime.strptime(start_date, f"%Y-%m-%d")
        end_date = datetime.strptime(end_date, f"%Y-%m-%d")
        # Plot Precipitation
        precipitation_save_path = f'./app/static/charts/precipitation_{city.replace(" ", "_")}.png'
        self.plot_precipitation(city, start_date, end_date, save_path=precipitation_save_path)

        #X = [...]  # Your feature matrix
        #y = [...]  # Your target variable

        predictions_save_path = f'./app/static/charts/predictions_{city.replace(" ", "_")}.png'
        #self.plot_predictions(X, y, save_path=predictions_save_path)

        precipitation_save_path = f'../static/charts/precipitation_{city.replace(" ", "_")}.png'
        predictions_save_path = f'../static/charts/predictions_{city.replace(" ", "_")}.png'
        return [precipitation_save_path, predictions_save_path]
    
    def create_dashboard_enddevice(self, data):
        if not data:
            return "No data found."

        # Extracting data for charts
        dates = [entry['date'] for entry in data]
        #dates = [datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ") for date in dates]
        storage_used = [entry['storage_used'] for entry in data]
        storage = [entry['storage'] for entry in data][0]
        ram_used = [entry['ram_used'] for entry in data]
        ram = [entry['ram'] for entry in data][0]
        cpu_percentage = [entry['cpu'] for entry in data]
        
        print("dates : ",dates)
        print("storage :", storage)
        print("ram :", ram)

        # Creating and saving the Storage Used chart
        plt.figure(figsize=(10, 5))
        plt.plot(dates, storage_used, label='Storage Used', marker='o')
        plt.xlabel('Date')
        plt.ylabel('Storage Used')
        plt.title('Storage Used Over Time')
        plt.xticks(rotation=45)
        plt.legend()
        plt.ylim(0, storage)  # Set y-axis limits
        storage_chart_path = './app/static/charts/storage_chart.png'
        plt.savefig(storage_chart_path, bbox_inches='tight')
        storage_chart_path = '../static/charts/storage_chart.png'
        plt.close()

        # Creating and saving the RAM Used chart
        plt.figure(figsize=(10, 5))
        plt.plot(dates, ram_used, label='RAM Used', marker='o', color='orange')
        plt.xlabel('Date')
        plt.ylabel('RAM Used')
        plt.title('RAM Used Over Time')
        plt.xticks(rotation=45)
        plt.legend()
        plt.ylim(0, ram)  # Set y-axis limits
        ram_chart_path = './app/static/charts/ram_chart.png'
        plt.savefig(ram_chart_path, bbox_inches='tight')
        ram_chart_path = '../static/charts/ram_chart.png'
        plt.close()

        # Creating and saving the CPU Percentage chart
        plt.figure(figsize=(10, 5))
        plt.plot(dates, cpu_percentage, label='CPU Percentage', marker='o', color='green')
        plt.xlabel('Date')
        plt.ylabel('CPU Percentage')
        plt.title('CPU Percentage Over Time')
        plt.xticks(rotation=45)
        plt.legend()
        cpu_chart_path = './app/static/charts/cpu_chart.png'
        plt.savefig(cpu_chart_path, bbox_inches='tight')
        cpu_chart_path = '../static/charts/cpu_chart.png'
        plt.close()

        # Return paths to the saved charts
        return storage_chart_path, ram_chart_path, cpu_chart_path