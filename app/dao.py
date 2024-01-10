from pymongo import MongoClient

class dao:
    client=MongoClient('mongodb://localhost:27017')
    def __init__(self) -> None:
        self.db=dao.client["monitoring"]
        self.account=self.db["accounts"]
        self.clients=self.db["clients"]
    def getClients(self):
        objects:list=[]
        for obj in self.clients.find():
            objects.append(obj)
        return objects
    def addClient(self,object):
        self.clients.insert_one(object)
    def delete(self,id):
        self.clients.delete_one({"_id":id})
    def update(self,object):
        self.clients.update_one({'_id':object['_id']},{'$set':object})
    def exist(self,object):
        results=self.clients.find_one({'_id':object['_id']})
        return results
    # def addUser(self,object):
    #     self.account.insert_one(object)
    def Authentificate(self,login,password):
        result=self.account.find_one({'username':login,'password':password})
        if result != None:
            return True
        else :
            return False