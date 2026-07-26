import re 
class Parser:
    def __init__(self):
        self.commands = ['set', 'get', 'del','keys','flushall','exists','incr','decr','ttl','append','strlen'
                         ,'type','persist']

    def _clean_text(self, text: str):
        text = text.lower()
        text =text.strip()

        return text
        
    def split_data(self,text:str) -> list:

        text_list =text.split() 
        if text_list[0] not in self.commands:
            return []
        
        return text_list

    
    def process(self,text):

        text = self._clean_text(text) 
        text_list = self.split_data(text)
        return text_list