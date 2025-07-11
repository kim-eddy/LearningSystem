from .models import LearningPath, LearningGoal, LearningPathTopic

def build_learning_path(student, course, weak_topics, scraped_data):
    path = LearningPath.objects.create(student=student, course=course)
    
    for order, topic in enumerate(weak_topics):
        path_topic = LearningPathTopic.objects.create(
            path=path,
            topic=topic,
            order=order
        )
        
        # Fix: scraped_data should be a list, not a dict keyed by topic name
        # If you want to filter resources by topic, do so here
        topic_resources = []
        if isinstance(scraped_data, dict):
            topic_resources = scraped_data.get(topic.name, [])
        elif isinstance(scraped_data, list):
            # Filter resources that match the topic name in their title or description
            topic_resources = [
                res for res in scraped_data
                if topic.name.lower() in res.get('title', '').lower() or
                   topic.name.lower() in res.get('description', '').lower()
            ]
        else:
            topic_resources = []

        for res in topic_resources:
            LearningGoal.objects.create(
                topic=topic,
                title=res.get('title', ''),
                url=res.get('url', ''),
                source=res.get('source', ''),
                content_type=res.get('type', 'video'),
                difficulty=res.get('difficulty', 'medium')
            )
    
    return path
