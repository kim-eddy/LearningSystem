from celery import shared_task
from .Filter import fetch_mysql_data, fetch_mongo_data, fetch_redis_data, format_data_for_gemini, call_gemini
import redis
import mysql.connector

@shared_task
def generate_recommendations_task(user, interests):
    data = fetch_mysql_data() + fetch_mongo_data() + fetch_redis_data()
    formatted = format_data_for_gemini(data)
    interests_str = ', '.join(interests)
    

    prompt = f"""
User '{user.id}' is interested in: {interests_str}
Below are learning resources. Based on their interests, recommend 5 materials in JSON format.

Materials:
{formatted}
"""
    results = call_gemini(prompt)

    # Defensive: Ensure results is a list of dicts
    if not isinstance(results, list):
        return {"status": "error", "message": f"Gemini did not return a list. Got: {type(results)} {results}"}
    for item in results:
        if not isinstance(item, dict):
            return {"status": "error", "message": f"Gemini returned non-dict item: {item}"}

    # Store to MySQL
    try:
        conn = mysql.connector.connect(
            host="ballast.proxy.rlwy.net",
            user="root",
            password="JOwJHNqsuEITqzqJUNNVajFwaDPznwRO",
            database="railway"
        )
        cursor = conn.cursor()
        for item in results:
            try:
                cursor.execute("""
                    INSERT INTO resources (title, description, source, url)
                    VALUES (%s, %s, %s, %s)
                """, (item.get('title', ''), item.get('description', ''), item.get('source', ''), item.get('url', '')))
            except Exception as e:
                return {"status": "error", "message": f"MySQL insert error: {str(e)} for item: {item}"}
        conn.commit()
        conn.close()
    except Exception as e:
        return {"status": "error", "message": f"MySQL error: {str(e)}"}

    # Store to Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        for item in results:
            key = f"material:{item.get('title', '')}"
            r.hset(key, mapping={
                "title": item.get('title', ''),
                "description": item.get('description', ''),
                "source": item.get('source', ''),
                "url": item.get('url', '')
            })
    except Exception as e:
        return {"status": "error", "message": f"Redis error: {str(e)}"}

    return {"status": "success", "saved": len(results)}

from celery import shared_task
from .learning_path import build_learning_path
from .models import Topic, Student_Profile, Course
from .scrapper import scrape_topic_data
from .Filter import filter_resources

@shared_task
def regenerate_learning_path_task(username, topic_id):
    try:
        topic = Topic.objects.get(id=topic_id)
        user = Student_Profile.objects.get(id=user.id)
        course = topic.course

        scraped = scrape_topic_data([topic.name])
        filtered = filter_resources(scraped)

        build_learning_path(user, course, [topic], filtered)

        return f"Regenerated path for {username} on topic {topic.name}"
    except Exception as e:
        return f"Error: {str(e)}"
