import redis

<<<<<<< HEAD
r = redis.StrictRedis(redis://default:LKIQbWKQHXlHIcrNAXAhJBGPGjSCuXAf@redis.railway.internal:6379)
=======
r = redis.StrictRedis(host='redis.railway.internal', port=6379, db=0)

>>>>>>> c27d540cc3cb36974a217ffd662c64599aadfb5f
def save_student_session(user, data):
    r.set(f"session:{user.id}", data)

def get_student_session(user):
    return r.get(f"session:{user.id}")
