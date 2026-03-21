import time

CACHE = {}
TTL = 300  # 5 minutes

def cache_get(key):
    if key in CACHE:
        value, expiry = CACHE[key]
        if time.time() < expiry:
            return value
        else:
            del CACHE[key]
    return None

def cache_set(key, value):
    CACHE[key] = (value, time.time() + TTL)
