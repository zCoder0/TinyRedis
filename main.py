from src.parser.parser import Parser
from src.engine.data_ingestion import StorageEngine
from src.config import Settings


if __name__ == '__main__':

    parser = Parser()
    storage_enginee = StorageEngine()
    while True:
        text = input("Text (Eg. SET name age): ")
        text_list = parser.process(text)

        print(storage_enginee.process(text_list))