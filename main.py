from typing import Union
from fastapi import FastAPI
from analyzer import analyze
app = FastAPI()

@app.get("/")
def read_root():
    return "Email Scanner API Server"

@app.get("/scan")
async def scan():
    analyze()
    return "done"