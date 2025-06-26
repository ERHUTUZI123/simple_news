# This file makes the app directory a Python package 

import redis
import os

# Redis connection URL, can be set via environment variable or default to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL) 