from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from routes.client import router as client_router
from routes.worker import router as worker_router

app = FastAPI()

routers = [client_router, worker_router]

for router in routers:
    app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uvicorn.run(app, host="0.0.0.0", port=443, ssl_certfile="../../instrio.crt", ssl_keyfile="../../instrio-nopass.key")