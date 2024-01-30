import mysql.connector as my
from datetime import datetime, timedelta
from pymongo import MongoClient
class Dao:
    def __init__(self) -> None:
        self.con = my.connect(
            user="root",
            password="",
            database="monitoring"
        )
        self.cursor = self.con.cursor()

    def getClients(self):
        objects = []
        try:
            self.cursor.execute("SELECT * FROM client")
            rows = self.cursor.fetchall()
            if rows is not None:
                for row in rows:
                    objects.append({'id': row[0], 'name': row[1], 'address': row[2], 'type': row[3], 'latitude':row[4], 'longitude':row[5]})
        except Exception as e:
            print(f"Error in getclient: {e}")
        finally:
            return objects

    def getMaxId(self):
        self.cursor.execute("SELECT MAX(id) FROM client")
        result = self.cursor.fetchone()
        return result[0] if result and result[0] is not None else None

    def addClient(self, obj):
        query = "INSERT INTO client (name, address, type, latitude, longitude) VALUES (%s,%s, %s, %s, %s)"
        values = (obj['name'], obj['address'], obj['type'], obj['latitude'], obj['longitude'])
        self.cursor.execute(query, values)
        self.con.commit()
        
    def addCityClient(self, obj):
        query = "INSERT INTO client (name, type, latitude, longitude) VALUES (%s, %s, %s, %s)"
        values = (obj['name'], obj['type'], obj['latitude'], obj['longitude'])
        self.cursor.execute(query, values)
        self.con.commit()

    def delete(self, id):
        query = "DELETE FROM client WHERE id = %s"
        self.cursor.execute(query, (id,))
        self.con.commit()

    def selectClient(self, id):
        query = "SELECT * FROM client WHERE id = %s"
        self.cursor.execute(query, (id,))
        result = self.cursor.fetchone()
        return {'id': result[0], 'name': result[1], 'address': result[2], 'type': result[3], 'latitude':result[4], 'longitude':result[5]} if result else None

    def updateClient(self, obj):
        query = "UPDATE client SET name = %s, address = %s, latitude = %s, longitude = %s WHERE id = %s"
        values = (obj['name'], obj['address'], obj['latitude'], obj['longitude'])
        self.cursor.execute(query, values)
        self.con.commit()

    def Authentificate(self, login, password):
        query = "SELECT * FROM account WHERE username = %s AND password = %s"
        values = (login, password)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return True if result else False
    
    def addEndDevice(self, device):
        try:
            query = "INSERT INTO EndDevice (id_client, storage_used, storage, ram_used, ram, cpu, date ) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            values = (device['id_client'], device['storage_used'], device['storage'], device['ram_used'], device['ram'], str(round(float(device['cpu']), 2)), device['date'])
            self.cursor.execute(query, values)
            self.con.commit()
        except Exception as e:
            print(f"Error in addEndDevice: {e}")


    def getEndDevices(self, id):
        objects = []
        try:
            query = "SELECT * FROM EndDevice WHERE id_client = %s"
            self.cursor.execute(query, (id,))
            rows = self.cursor.fetchall()
            if rows is not None:
                for row in rows:
                    objects.append({'id': row[0], 'date': row[1], 'storage': row[2], 'storage_used': row[3], 'ram': row[4], 'ram_used': row[5], 'cpu': row[6], 'id_client': row[7]})
        except Exception as e:
            print(f"Error in getEndDevices: {e}")
        finally:
            return objects

    def getEndDevicesByDate(self, id, start_date, end_date):
        objects = []
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

            query = "SELECT * FROM EndDevice WHERE id_client = %s AND date BETWEEN %s AND %s"
            values = (id, start_datetime, end_datetime)
            self.cursor.execute(query, values)
            rows = self.cursor.fetchall()
            if rows is not None:
                for row in rows:
                    objects.append({'id': row[0], 'date': row[1], 'storage': row[2], 'storage_used': row[3], 'ram': row[4], 'ram_used': row[5], 'cpu': row[6], 'id_client': row[7]})
        except Exception as e:
            print(f"Error in getEndDevicesByDate: {e}")
        finally:
            return objects

    def addIOT(self, iot):
        try:
            query = "INSERT INTO IOT (mac, date, temperature, id_client) VALUES (%s, %s, %s, %s)"
            values = (iot['mac'], iot['date'], iot['temperature'], iot['id_client'])
            self.cursor.execute(query, values)
            self.con.commit()
        except Exception as e:
            print(f"Error in addIOT: {e}")

    def getIOTs(self, id):
        objects = []
        try:
            query = "SELECT * FROM IOT WHERE id_client = %s"
            self.cursor.execute(query, (id,))
            rows = self.cursor.fetchall()
            if rows is not None:
                for row in rows:
                    objects.append({'id': row[0], 'mac': row[1], 'date': row[2], 'temperature': row[3], 'id_client': row[4]})
        except Exception as e:
            print(f"Error in getIOTs: {e}")
        finally:
            return objects

    def getIOTByMac(self, mac):
        try:
            query = "SELECT * FROM IOT WHERE mac = %s"
            self.cursor.execute(query, (mac,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error in getIOTByMac: {e}")

    def getIOTDataByMac(self, mac):
        objects = []
        try:
            query = "SELECT * FROM IOT WHERE mac = %s"
            self.cursor.execute(query, (mac,))
            rows = self.cursor.fetchall()
            if rows is not None:
                for row in rows:
                    objects.append({'id': row[0], 'mac': row[1], 'date': row[2], 'temperature': row[3], 'id_client': row[4]})
        except Exception as e:
            print(f"Error in getIOTDataByMac: {e}")
        finally:
            return objects

    def getIOTByMacAndDate(self, mac, start_date, end_date):
        objects = []
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

            query = "SELECT * FROM IOT WHERE mac = %s AND date BETWEEN %s AND %s"
            values = (mac, start_datetime, end_datetime)
            self.cursor.execute(query, values)
            rows = self.cursor.fetchall()
            if rows is not None:
                for row in rows:
                    objects.append({'id': row[0], 'mac': row[1], 'date': row[2], 'temperature': row[3], 'id_client': row[4]})
        except Exception as e:
            print(f"Error in getIOTByMacAndDate: {e}")
        finally:
            return objects

# Example Usage
if __name__=="__main__":
    dao = Dao()
    client=MongoClient('mongodb://localhost:27017')
    db=client["monitoring"]
    enddevices=db["EndDevice"]
    iots=db["IOT"]
    for obj in iots.find():
        dao.addIOT({'mac': obj['MAC'], 'date': obj['date'], 'temperature': obj['temperature'], 'id_client': obj['id']})
