from src.parser.load_save_parser import load, save
import time
from src.config import Settings
import threading
import json,sys
from src.exception import ProjectException

class StorageEngine:

    def __init__(self):

        self.redis_data = load(Settings.redis_data_path) or {}
        self.redis_expiry_data = load(Settings.expiry_data_path) or {}
        self.redis_data_path = Settings.redis_data_path
        self.redis_expiry_data_path =Settings.expiry_data_path
        self._expiry_lock = threading.Lock()
        self._timer = None
        self.run_expiry_thread()

    def save_all(self):
        return (save(self.redis_data_path, self.redis_data) and 
                save(self.redis_expiry_data_path , self.redis_expiry_data)
                )
    
    def _normalize_value(self,val):
        try:
            val = int(val)
        except ValueError:
            try:
                val = float(val)
            except ValueError:
                val = val

        return val

    def add_data(self,data:list):

        try:
            dict_data = dict(zip(data[::2],data[1::2]))

            for key,value in dict_data.items():
                dict_data[key]=self._normalize_value(value)
            
            key_detail=[]
        
            if "ex" in dict_data.keys():
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
        
        except Exception as e:
            print(ProjectException(e,sys))
            
    def del_data(self,key):
        try:
            if not self.is_key_exist(key):
                return -2 
            
            poped_data = self.redis_data.pop(key)
            if key in self.redis_expiry_data.keys():
                self.redis_expiry_data.pop(key)
            print(f"Deleted sucessfully {key}:{poped_data}")
            return self.save_all()
        except Exception as e:
            print(ProjectException(e,sys))
            
    def get_data(self, key):

        if not self.is_key_exist(key):
            return -2 
        
        return self.redis_data.get(key)
    
    def is_key_exist(self,key):
        return key in self.redis_data

    def list_keys(self):
        return self.redis_data.keys()
    
    def flushall(self):
        try:
            self.redis_data.clear()
            self.redis_expiry_data.clear()
            return self.save_all()
        except Exception as e:
            print(ProjectException(e,sys))
            
    def incr(self,key):
        try:
            if not self.is_key_exist(key):
                print("Not exists")
                return None 

            val=self.redis_data[key]
            if isinstance(val, int):
                self.redis_data[key]= (val+1)
                return save(self.redis_data_path,self.redis_data)
        except Exception as e:
            print(ProjectException(e,sys))
            
    def decr(self,key):
        try:
            if not self.is_key_exist(key):
                print("Not exists")
                return None 
            val=self.redis_data[key]
            if isinstance(val, int):
                self.redis_data[key]= (val-1)
                return save(self.redis_data_path,self.redis_data)
        except Exception as e:
            print(ProjectException(e,sys))
            
    def _silent_save(self):
        try:
            with open(self.redis_data_path, 'w', encoding="utf8") as f:
                json.dump(self.redis_data, f, indent=4)
            with open(self.redis_expiry_data_path, 'w', encoding="utf8") as f:
                json.dump(self.redis_expiry_data, f, indent=4)
        except Exception as e:
            print(ProjectException(e,sys))

    def run_expiry_thread(self):
        try:
            with self._expiry_lock:
                to_delete = [k for k in self.redis_expiry_data]
                for key in to_delete:
                    if int(self.redis_expiry_data[key][0]) <= time.time() - float(self.redis_expiry_data[key][1]):
                        self.redis_data.pop(key, None)
                        self.redis_expiry_data.pop(key, None)
            self._silent_save()
            self._timer = threading.Timer(1.0, self.run_expiry_thread)
            self._timer.start()
        except Exception as e:
            print(ProjectException(e,sys))

    def shutdown(self):
        if self._timer is not None:
            self._timer.cancel()

    def ttl(self,key):
        try:
            if self.redis_data.get(key) is None:
                return -2
            
            if not self.redis_expiry_data.get(key):
                return -1 

            remaining_time =  int(self.redis_expiry_data[key][0])  - (time.time()-self.redis_expiry_data[key][1]) 
            return int(remaining_time)

        except Exception as e:
            print(ProjectException(e,sys))
        
    def append(self,data):
        try:
            dict_data = dict(zip(data[::2], data[1::2])) 
            
            for k in dict_data.keys():
                if self.redis_data.get(k):
                    if  isinstance(self.redis_data[k], str):
                        self.redis_data[k] += str(dict_data[k])
                    else:
                        return False
                else:
                    self.redis_data[k] = dict_data[k]

            return save(self.redis_data_path ,self.redis_data)
        except Exception as e:
            print(ProjectException(e,sys))

    def process(self,data:list):

        try:
            if data[0] == 'set':
                if (len(data)-1)%2 !=0 or len(data) == 1:
                    print("Invalid Input")
                    return 
                return self.add_data(data[1:])

            elif data[0] == 'del':
                return self.del_data(data[1])

            elif data[0] == 'get':
                if len(data) == 1:
                    return self.redis_data
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
                return self.decr(data[1])

            elif data[0] == 'ttl':
                return self.ttl(data[1])

            elif data[0] == 'append':
                if len(data) == 1:
                    print("Invalid Input")
                    return
                return self.append(data[1:])

            elif data[0] == 'strlen':
                if len(data) == 1:
                    print("Invalid Input")
                    return
                if not self.is_key_exist(data[1]):
                    return -2

                if isinstance(self.redis_data[data[1]],str):
                    return len(self.redis_data[data[1]])
                return -1

            elif data[0] == 'type':
                if len(data) == 1:
                    print("Invalid Input")
                    return 
                if not self.is_key_exist(data[1]):
                    return -2
                return type(self.redis_data[data[1]]).__name__ 

        except Exception as e:
            print(ProjectException(e,sys))
            