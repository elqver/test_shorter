import asyncio

from fastapi import FastAPI
import redis


app = FastAPI()
cache = redis.Redis(host='redis', port=6379)
