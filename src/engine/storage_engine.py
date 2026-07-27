from src.parser.load_save_parser import load, save
import time
from src.config import Settings
import threading
import json,sys
from src.exception import ProjectException
from src.engine.redis_value import RedisValue

from src.engine.linked_list import DoublyLinkedList

class StorageEngine:

    def __init__(self):

        self.redis_data = load(Settings.redis_data_path) or {}
        self.redis_expiry_data = load(Settings.expiry_data_path) or {}
        self.redis_data_path = Settings.redis_data_path
        self.redis_expiry_data_path =Settings.expiry_data_path
        self._expiry_lock = threading.Lock()
        self._timer = None
        self.list_values = {}
        for key, val in self.redis_data.items():
            if val.get("type") == "list":
                dll = DoublyLinkedList()
                for item in val.get("value", []):
                    dll.rpush(item)
                self.list_values[key] = dll
        self.run_expiry_thread()

    def save_all(self):
        for key, dll in self.list_values.items():
            self.redis_data[key]["value"] = dll.to_list()
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

            for key,value in dict_data.items():
                redis_value = RedisValue(value)
                self.redis_data[key] = redis_value.to_dict()

            return self.save_all()
        
        except Exception as e:
            print(ProjectException(e,sys))
            
    def del_data(self,key):
        try:
            if not self.is_key_exist(key):
                return -2 
            
            poped_data = self.redis_data.pop(key)
            self.list_values.pop(key, None)
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
            self.list_values.clear()
            return self.save_all()
        except Exception as e:
            print(ProjectException(e,sys))
            
    def incr(self,key):
        try:
            if not self.is_key_exist(key):
                return -2

            val=self.redis_data[key]
            if val.get('type') == 'integer':
                val['value']+=1
                return save(self.redis_data_path,self.redis_data)
            return -2
        except Exception as e:
            print(ProjectException(e,sys))
            
    def decr(self,key):
        try:
            if not self.is_key_exist(key):
                print("Not exists")
                return None 
            val=self.redis_data[key]
            if val.get('type') == 'integer':
                val['value']-=1
                return save(self.redis_data_path,self.redis_data)
            return -2
        except Exception as e:
            print(ProjectException(e,sys))
            
    def _silent_save(self):
        try:
            for key, dll in self.list_values.items():
                self.redis_data[key]["value"] = dll.to_list()
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

            for k,v in dict_data.items():
                dict_data[k] = self._normalize_value(val=v)
        
            for k in dict_data.keys():
                if self.redis_data.get(k):
                    if self.redis_data[k].get('type') =='string':
                        self.redis_data[k]['value'] += dict_data[k]
                    else:
                        return False
                else:
                    redis_value = RedisValue(dict_data[k])
                    self.redis_data[k] = redis_value.to_dict()

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

                if self.redis_data[data[1]].get('type') == 'string':
                    return len(self.redis_data[data[1]].get('value'))
                
                return -1

            elif data[0] == 'type':
                if not self.is_key_exist(data[1]):
                    return -2
                return self.redis_data[data[1]].get('type')

            elif data[0] == 'rpush':
                if len(data) < 3:
                    return "Invalid Input"
                key = data[1]
                if not self.is_key_exist(key):
                    dll = DoublyLinkedList()
                    self.list_values[key] = dll
                    self.redis_data[key] = {"type": "list", "value": []}
                elif self.redis_data[key].get("type") != "list":
                    return "WRONG_TYPE Operation against a key holding the wrong kind of value"
                dll = self.list_values[key]
                for value in data[2:]:
                    dll.rpush(self._normalize_value(value))
                return self.save_all()

            elif data[0] == 'lpush':
                if len(data) < 3:
                    return "Invalid Input"
                key = data[1]

                if not self.is_key_exist(key):
                    dll = DoublyLinkedList()
                    self.list_values[key] = dll
                    self.redis_data[key] = {"type": "list", "value": []}
                elif self.redis_data[key].get("type") != "list":
                    return "WRONG_TYPE Operation against a key holding the wrong kind of value"
                dll = self.list_values[key]
                for value in data[2:]:
                    dll.lpush(self._normalize_value(value))
                return self.save_all()

            elif data[0] == 'lpop':
                if len(data) < 2:
                    return "Invalid Input"
                key = data[1]
                if not self.is_key_exist(key):
                    return -2
                if self.redis_data[key].get("type") != "list":
                    return "WRONG_TYPE Operation against a key holding the wrong kind of value"
                dll = self.list_values[key]
                value = dll.lpop()
                if dll.head is None:
                    self.list_values.pop(key, None)
                    self.redis_data.pop(key, None)
                    self.redis_expiry_data.pop(key, None)
                return self.save_all() and value

            elif data[0] == 'rpop':
                if len(data) < 2:
                    return "Invalid Input"
                key = data[1]
                if not self.is_key_exist(key):
                    return -2
                if self.redis_data[key].get("type") != "list":
                    return "WRONG_TYPE Operation against a key holding the wrong kind of value"
                dll = self.list_values[key]
                value = dll.rpop()
                if dll.head is None:
                    self.list_values.pop(key, None)
                    self.redis_data.pop(key, None)
                    self.redis_expiry_data.pop(key, None)
                return self.save_all() and value

            elif data[0] == 'lrange':
                if len(data) < 4:
                    return "Invalid Input"
                key = data[1]
                if not self.is_key_exist(key):
                    return -2
                if self.redis_data[key].get("type") != "list":
                    return "WRONG_TYPE Operation against a key holding the wrong kind of value"
                dll = self.list_values[key]
                items = dll.to_list()
                length = len(items)
                start = self._normalize_value(data[2])
                stop = self._normalize_value(data[3])
                if not isinstance(start, int) or not isinstance(stop, int):
                    return "Invalid Input"
                if start < 0:
                    start = max(length + start, 0)
                if stop < 0:
                    stop = max(length + stop, 0)
                if start >= length or start > stop:
                    return []
                stop = min(stop, length - 1)
                return items[start:stop + 1]
        except Exception as e:
            print(ProjectException(e,sys))
