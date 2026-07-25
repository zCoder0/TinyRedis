from src.parser.load_save_parser import load,save
import time
from src.config import Settings
import threading
class StorageEngine:

    def __init__(self):
        self.redis_data = load(Settings.redis_data_path) or {}
        self.redis_expiry_data = load(Settings.expiry_data_path) or {}
        self.redis_data_path = Settings.redis_data_path
        self.redis_expiry_data_path =Settings.expiry_data_path

    def save_all(self):
        return (save(self.redis_data_path, self.redis_data) and 
                save(self.redis_expiry_data_path , self.redis_expiry_data)
                )
    
    def add_data(self,data:list):

        dict_data = dict(zip(data[::2],data[1::2]))

        key_detail=[]
        if "ex" in dict_data.keys():
            print("Expiry key found")
            for key in dict_data.keys():
                if key == 'ex':
                    if not key_detail:
                        return "Invalid Input"
                    val = dict_data.pop('ex')
                    self.redis_expiry_data[key_detail.pop()]=(val,time.time())
                    key_detail=[]
                    break
                key_detail.append(key)

        self.redis_data.update(dict_data)
        return self.save_all()

    def del_data(self,key):

        if not self.is_key_exist(key):
            print("Key does not exist")
            return False
        
        poped_data = self.redis_data.pop(key)
        print(f"Deleted sucessfully {key}:{poped_data}")
        return self.save_all()

    def get_data(self, key):

        if not self.is_key_exist(key):
            print("Key does not exist")
            return False
        
        return self.redis_data[key]
    
    def is_key_exist(self,key):
        return False if key not in self.redis_data.keys() else True

    def list_keys(self):
        return self.redis_data.keys()
    
    def flushall(self):
        self.redis_data.clear()
        return self.save_all()

    def incr(self,key):

        if not self.is_key_exist(key):
            print("Not exists")
            return None 
        if self.redis_data[key].isdigital():
            self.redis_data[key]= int(self.redis_data[key])+1
        return self.save_all()

    def decr(self,key):

        if not self.is_key_exist(key):
            print("Not exists")
            return None 
        self.redis_data[key]= int(self.redis_data[key])-1
        return self.save_all()

    def run_expiry_thread(self):
        try:
            threading.Timer(1.0, self.run_expiry_thread).start()
            for key in self.redis_expiry_data.keys():
                if int(self.redis_expiry_data[key][0]) <= time.time()-float(self.redis_expiry_data[key][1]):
                    self.del_data(key)
                    self.redis_expiry_data.pop(key)
                    save(self.redis_expiry_data_path, self.redis_expiry_data)
        except Exception as e:
            print("error: ",e)
    def process(self,data:list):

        self.run_expiry_thread()

        if data[0] == 'set':
            if (len(data)-1)%2 !=0:
                print("Invalid Input")
                return 
            return self.add_data(data[1:])

        elif data[0] == 'del':
            return self.del_data(data[1])

        elif data[0] == 'get':
            return self.get_data(data[1])

        elif data[0] == 'keys':
            return self.list_keys()

        elif data[0] == 'flushall':
            return self.flushall()

        elif data[0] == 'exists':
            return self.is_key_exist(data[1])

        elif data[0] == 'incr':
            return self.incr(data[1])
        
        elif data[0] == 'decr':
            return self.incr(data[1])
