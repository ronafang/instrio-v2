from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import ssl
import os

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile="../../instrio.crt", keyfile="../../instrio-nopass.key")

from routes.client import router as client_router
from routes.worker import router as worker_router

app = FastAPI()

routers = [client_router, worker_router]

for router in routers:
    app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://instr.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uvicorn.run(app, host="0.0.0.0", port=443, ssl_context=ssl_context)