import json
from src.exception import ProjectException
import sys 
def load(path):

    try:
        with open(path,'r',encoding="utf8") as f:
            data = json.load(f)
        return data
    
    except Exception as e:
        print(ProjectException(e,sys))

def save(path,data):

    try:
        with open(path,'w',encoding="utf8") as f:
            json.dump(data,f,indent=4)

        print("Successfully saved!...")
        return True
    except Exception as e:
        print(ProjectException(e,sys))
        