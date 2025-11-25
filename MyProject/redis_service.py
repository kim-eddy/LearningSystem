import redis

r = redis.StrictRedis(host='redis.railway.internal', port=6379, db=0)

def save_student_session(user, data):
    r.set(f"session:{user.id}", data)

def get_student_session(user):
    return r.get(f"session:{user.id}")
