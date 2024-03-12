from redis import Redis
import os
redis = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            decode_responses=True,
            db=0,
        )

data = redis.hgetall("logs")
print(data)