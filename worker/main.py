import asyncio
import aiohttp
from collections import deque
from process import process
import base64
from io import BytesIO
import os
from dotenv import load_dotenv
load_dotenv()

KEY = os.getenv("KEY")
NUM_WORKERS = int(os.getenv("NUM_WORKERS", 4))

API_BASE_URL = "https://api.instr.io"
POLL_INTERVAL = 0.25

task_queue = deque()

async def poll_task():
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        while True:
            try:
                async with session.get(f"{API_BASE_URL}/task?key={KEY}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("hasTask"):
                            tid = data.get("tid")
                            raw_audio = data.get("raw")
                            print(f"Task received: {tid}")
                            task_queue.append((tid, raw_audio))
                    else:
                        print(f"Failed to fetch task: {response.status}")
            except Exception as e:
                print(f"Error polling task: {e}")
            await asyncio.sleep(POLL_INTERVAL)

async def worker(worker_id):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        while True:
            if task_queue:
                tid, raw_audio_base64 = task_queue.popleft()
                print(f"Worker {worker_id} processing task: {tid}")
                try:
                    audio_data = BytesIO(base64.b64decode(raw_audio_base64))
                    
                    processed_audio = process(audio_data).getvalue()
                    
                    data = aiohttp.FormData()
                    data.add_field('completion', processed_audio, filename='audio.pcm', content_type='audio/pcm')
                    data.add_field('tid', tid)
                    async with session.put(f"{API_BASE_URL}/task", data=data) as response:
                        if response.status == 200:
                            print(f"Worker {worker_id} completed task {tid} successfully")
                        else:
                            print(f"Worker {worker_id} failed to complete task {tid}: {response.status}")
                except Exception as e:
                    print(f"Worker {worker_id} error processing task {tid}: {e}")
            else:
                await asyncio.sleep(0.1)

async def main():
    workers = [worker(worker_id) for worker_id in range(NUM_WORKERS)]
    await asyncio.gather(poll_task(), *workers)

# Run the main function
asyncio.run(main())
