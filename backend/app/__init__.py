# This file makes the app directory a Python package 

import os

# Redis connection URL, can be set via environment variable or default to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Make redis optional - if not available, create a mock client
try:
    import redis
    redis_client = redis.from_url(REDIS_URL)
    # Test the connection
    redis_client.ping()
    print("✅ Redis connected successfully")
except ImportError:
    print("⚠️ Redis not available, using mock client")
    # Create a mock redis client for when redis is not available
    class MockRedisClient:
        def get(self, key):
            return None
        def setex(self, key, time, value):
            pass
        def set(self, key, value):
            pass
        def ping(self):
            return True
    redis_client = MockRedisClient()
except Exception as e:
    print(f"⚠️ Redis connection failed: {e}, using mock client")
    # Create a mock redis client for when redis connection fails
    class MockRedisClientFallback:
        def get(self, key):
            return None
        def setex(self, key, time, value):
            pass
        def set(self, key, value):
            pass
        def ping(self):
            return True
    redis_client = MockRedisClientFallback() 