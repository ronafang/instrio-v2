from collections import deque
from cachetools import TTLCache
import threading
import time
import uuid

class TaskQueue():
    def __init__(self):
        self.q = deque()
        self.completed = TTLCache(ttl=20, maxsize=100)
        self.events = TTLCache(ttl=40, maxsize=100)
        self.lock = threading.Lock()
    
    def append(self, raw, event):
        tid =  str(uuid.uuid4())
        with self.lock:
            self.q.append( {"time": time.time(), "raw": raw, "tid": tid} )
            self.events[tid] = event
        return tid
    
    def get(self, timeout=20):
        while self.q:
            task = self.q.popleft()
            if time.time() - task["time"] > timeout:
                continue
            return task
        return None
    
    def complete(self, tid, instr):
        self.completed[tid] = instr
        self.events[tid].set()
        del self.events[tid]
    
    def fetch(self, tid):
        if tid in self.completed:
            result = self.completed[tid]
            del self.completed[tid]
            return result
        else:
            return None

