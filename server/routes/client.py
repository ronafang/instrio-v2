from fastapi import APIRouter, Depends, UploadFile, File
from util.queue import TaskQueue
from dependencies import get_tq
from starlette.responses import Response
import asyncio
from io import BytesIO
router = APIRouter()


@router.post("/task")
async def post_task(file: UploadFile = File(...), tq: TaskQueue = Depends(get_tq)):
    raw = BytesIO(await file.read())
    event = asyncio.Event()
    
    tid = tq.append(raw=raw, event=event)

    await event.wait()
    
    result = tq.fetch(tid)
    print(result)
    
    if result:
        return Response(content=result.getvalue(), media_type=file.content_type, headers={
            'Content-Disposition': f"attachment; filename=\"{file.filename}\""
        })
    else:
        raise "something is wrong"
