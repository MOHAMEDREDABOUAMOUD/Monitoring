from dao import Dao
from business import Business
services = Business()
daoo = Dao()

#from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

def job():
    cpu_percentage = services.get_cpu_percentage('127.0.0.1', 'public')
    disk_storage_info = services.get_disk_storage_info('127.0.0.1', 'public')
    data = {'id': 1, 'date': datetime.now(), 'storage': disk_storage_info[0], 'storage_used': disk_storage_info[1],
           'ram': disk_storage_info[2], 'ram_used': disk_storage_info[3], 'cpu': cpu_percentage}
    daoo.addEndDevice(data)
    print("add one")

while True:
    job()
    time.sleep(30)