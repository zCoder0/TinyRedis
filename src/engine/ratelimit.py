import time 
from collections import deque
class RateLimit:

    def __init__(self,MAX_RATELIMIT=5, TIM_WINDOW=10):
       self.MAX_RATELIMIT = MAX_RATELIMIT
       self.TIME_WINDOW = TIM_WINDOW
       self.queue = deque()

    def rateLimit(self,request):

        while self.queue and request - self.queue[0] >= self.TIME_WINDOW:
            self.queue.popleft()
            
        if len(self.queue) >= self.MAX_RATELIMIT:
            return False

        self.queue.append(request)
        return True
