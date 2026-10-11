import os
import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Connect to the redis container by its compose service name "redis".
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.post("/hit/{key}")
def hit(key: str):
    # INCR is atomic and stored in Redis, so the count survives restarts
    count = r.incr(key)
    return {"key": key, "count": count}


@app.get("/count/{key}")
def count(key: str):
    value = r.get(key)                       # None if the key was never hit
    return {"key": key, "count": int(value) if value is not None else 0}


@app.get("/healthz")
def healthz():
    try:
        r.ping()                             # actually ask Redis if it's alive
        return {"status": "ok", "redis": "up"}
    except Exception:
        return {"status": "error", "redis": "down"}
