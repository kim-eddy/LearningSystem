import redis

# Hardcoded Redis connection (for testing)
r = redis.StrictRedis(
    host='mainline.proxy.rlwy.net',
    port=11017,
    password='LKIQbWKQHXlHIcrNAXAhJBGPGjSCuXAf',
    db=0,
    decode_responses=True
)

def save_student_session(user, data):
    r.set(f"session:{user.id}", data)

def get_student_session(user):
    return r.get(f"session:{user.id}")
