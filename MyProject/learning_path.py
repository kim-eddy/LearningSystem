from .models import LearningPath, LearningGoal, LearningPathTopic

def build_learning_path(student, course, ordered_topics, scraped_data):
    # Create a goal for this path
    goal = LearningGoal.objects.create(
        student=student,
        title=f"Personalized Path for {course.title}",
        description="Auto-generated learning path based on your assessment."
    )
    for order, topic in enumerate(ordered_topics):
        LearningPath.objects.create(
            goal=goal,
            topic=topic,
            student=student,
            course=course,
            order=order,
            status='not_started',
            recommended_by_ai=True
        )
    return goal
