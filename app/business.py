#from pysnmp.hlapi import *
from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, getCmd, nextCmd, ObjectType, ObjectIdentity

# Add any additional components you need from pysnmp.hlapi
from pysnmp.hlapi import getCmd, nextCmd, ObjectType, ObjectIdentity

# Now you can use the imported components in your code
ErrorIndication, ErrorStatus, ErrorIndex, varBinds = next(
    getCmd(SnmpEngine(),
           CommunityData('public'),
           UdpTransportTarget(('localhost', 161)),
           ContextData(),
           ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0')))
)

# Continue using other components as needed

import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from sklearn.linear_model import LinearRegression
import numpy as np
import io

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
            
        print(storage, usedStorage)
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

    def get_precipitation_history(self, latitude, longitude, start_date, end_date):
        print(f"lat : {latitude}, log : {longitude}, start_date : {start_date}, end_date : {end_date}")
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
    
    def get_predictions(self, latitude, longitude):
        end_date = datetime.now() - timedelta(days=2)
        start_date = end_date - timedelta(days=14)
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')  # Change frequency to hourly

        temperature_data = self.get_precipitation_history(latitude, longitude, start_date, end_date)

        # Reshape the temperature data for training
        X = np.array(range(len(temperature_data))).reshape(-1, 1)
        y = temperature_data

        # Create a linear regression model
        model = LinearRegression()

        # Train the model
        model.fit(X, y)

        # Make predictions for the next 7 days (or 7 hours)
        X_future = np.array(range(len(temperature_data), len(temperature_data) + 7 * 24)).reshape(-1, 1)  # Change 7 to the desired number of days
        future_predictions = model.predict(X_future)

        return future_predictions
    
    def get_coordinates(self, city_name):
        geolocator = Nominatim(user_agent="monitoring")
        location = geolocator.geocode(city_name)
        return (location.latitude, location.longitude)

    def create_dashboard_city(self, latitude, longitude, start_date, end_date):
        
        start_date = datetime.strptime(start_date, f"%Y-%m-%d")
        end_date = datetime.strptime(end_date, f"%Y-%m-%d")
        precipitation_history = self.get_precipitation_history(latitude, longitude, start_date, end_date)
        
        start_date_predictions = datetime.now().strftime(f"%Y-%m-%d")
        end_date_predictions = (datetime.now() + timedelta(days=7)).strftime(f"%Y-%m-%d")
        predictions = self.get_predictions(latitude, longitude)
        
        date_range_1 = pd.date_range(start=start_date, end=end_date, freq='D')
        date_range_2 = pd.date_range(start=start_date_predictions, end=end_date_predictions, freq='D')

        # Convert datetime objects to strings
        date_range_1_str = date_range_1.strftime('%Y-%m-%d').tolist()
        date_range_2_str = date_range_2.strftime('%Y-%m-%d').tolist()
        
        #print(f"{precipitation_history} {predictions}")
        
        return precipitation_history, predictions, date_range_1_str, date_range_2_str
    
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

        # Creating and saving the Storage Used chart
        plt.figure(figsize=(10, 5))
        plt.plot(dates, storage_used, label='Storage Used', marker='o')
        plt.xlabel('Date')
        plt.ylabel('Storage Used')
        plt.title('Storage Used Over Time')
        plt.xticks(rotation=45)
        plt.legend()
        plt.ylim(0, storage)  # Set y-axis limits
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.clf()
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
        img_buffer2 = io.BytesIO()
        plt.savefig(img_buffer2, format='png')
        img_buffer2.seek(0)
        plt.clf()
        plt.close()

        # Creating and saving the CPU Percentage chart
        plt.figure(figsize=(10, 5))
        plt.plot(dates, cpu_percentage, label='CPU Percentage', marker='o', color='green')
        plt.xlabel('Date')
        plt.ylabel('CPU Percentage')
        plt.title('CPU Percentage Over Time')
        plt.xticks(rotation=45)
        plt.legend()
        img_buffer3 = io.BytesIO()
        plt.savefig(img_buffer3, format='png')
        img_buffer3.seek(0)
        plt.clf()
        plt.close()

        # Return paths to the saved charts
        return [img_buffer, img_buffer2, img_buffer3]
    
    def create_dashboard_IOT(self, data):
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(data)

        # Convert the 'date' column to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Sort the DataFrame by 'date'
        df = df.sort_values(by='date')

        # Plotting
        plt.figure(figsize=(10, 5))
        plt.plot(df['date'], df['temperature'], marker='o', linestyle='-', color='b')
        
        # Customize the plot
        plt.xlabel('Date')
        plt.ylabel('Temperature')
        plt.title('IOT Dashboard')
        plt.grid(True)
        plt.legend()
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.clf()
        plt.close()
        # temp_chart_path = "./app/static/charts/temp_chart.png"
        # plt.savefig(temp_chart_path)
        # temp_chart_path = "../static/charts/temp_chart.png"
        
        return img_buffer