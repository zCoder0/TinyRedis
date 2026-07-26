class RedisValue:

    def __init__(self, value):
        self.type = self.detect_type(value)
        self.value = value

    def detect_type(self,value):

        if isinstance(value,str):
            return "string"
        
        elif isinstance(value,int):
            return "integer"
        
        elif isinstance(value,float):
            return "float"

        else:
            return "unknown"

    def to_dict(self):
        return {
            "type":self.type,
            "value":self.value
        }
