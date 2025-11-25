import redis

r = redis.StrictRedis(redis://default:LKIQbWKQHXlHIcrNAXAhJBGPGjSCuXAf@redis.railway.internal:6379)
def save_student_session(user, data):
    r.set(f"session:{user.id}", data)

def get_student_session(user):
    return r.get(f"session:{user.id}")
