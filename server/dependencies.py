from fastapi import Depends
from util.queue import TaskQueue

tq = TaskQueue()

def get_tq() -> TaskQueue:
    return tq
