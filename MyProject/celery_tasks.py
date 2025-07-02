from celery import shared_task

@shared_task
def generate_learning_path(student_id):
    # Simulate a time-consuming AI process
    import time
    time.sleep(5)
    return f"Learning path generated for {student_id}"
