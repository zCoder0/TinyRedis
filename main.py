from src.parser.parser import Parser
from src.engine.storage_engine import StorageEngine
from src.config import Settings
from src.engine.ratelimit import RateLimit
import time
if __name__ == '__main__':

    parser = Parser()
    storage_enginee = StorageEngine()
    rate_limit = RateLimit()
    
    while True:
        text = input("Text (Eg. SET name age): ")
    
        if not rate_limit.rateLimit(time.time()):
            print("Rate limit exceeded")
            continue
        
        if text.strip().lower() in ('exit', 'quit'):
            storage_enginee.shutdown()
            print("Bye!")
            break

        if len(text.strip()) == 0:
            continue

        text_list = parser.process(text)
        if not text_list :
            print("Unknown command")
            continue
        print(storage_enginee.process(text_list))