from fastapi import FastAPI, UploadFile, File, Form, Depends, APIRouter, Request
from util.queue import TaskQueue
from dependencies import get_tq
import base64
from io import BytesIO

router = APIRouter()

@router.get("/task")
async def get_task(tq: TaskQueue = Depends(get_tq)):
    task = tq.get()
    if not task:
        return {"hasTask": False}
    else:
        return {
            "hasTask": True,
            "raw": base64.b64encode(task["raw"].getvalue()).decode("utf-8"),
            "tid": task["tid"]
        }

@router.put("/task")
async def put_task(request: Request, tq: TaskQueue = Depends(get_tq)):
    form = await request.form()
    
    tid = form.get("tid")
    
    completion = form.get("completion")
    print(completion)
    print("that was completion")
    if not completion:
        return {"error": "Completion file is required."}
    
    audio = BytesIO(await completion.read())
    tq.complete(tid, audio)
    return {}