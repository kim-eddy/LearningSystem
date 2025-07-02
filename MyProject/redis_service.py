import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

def save_student_session(student_id, data):
    r.set(f"session:{student_id}", data)

def get_student_session(student_id):
    return r.get(f"session:{student_id}")
