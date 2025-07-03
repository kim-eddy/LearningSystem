from celery import shared_task
from .gemini_recommender import fetch_mysql_data, fetch_mongo_data, fetch_redis_data, format_data_for_gemini, call_gemini
import redis
import mysql.connector

@shared_task
def generate_recommendations_task(username, interests, fav_sources):
    data = fetch_mysql_data() + fetch_mongo_data() + fetch_redis_data()
    formatted = format_data_for_gemini(data)
    interests_str = ', '.join(interests)
    fav_sources_str = ', '.join(fav_sources)

    prompt = f"""
User '{username}' is interested in: {interests_str}
Below are learning resources. Based on their interests and preferred sources ({fav_sources_str}), recommend 5 materials in JSON format.

Materials:
{formatted}
"""
    results = call_gemini(prompt)
    
    if isinstance(results, dict) and "error" in results:
        return {"status": "error", "message": results["error"]}

    # Store to MySQL
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="emmanuel",
            password="K7154muhell",
            database="LearningSystem"
        )
        cursor = conn.cursor()
        for item in results:
            cursor.execute("""
                INSERT INTO resources (title, description, source, url)
                VALUES (%s, %s, %s, %s)
            """, (item['title'], item['description'], item['source'], item['url']))
        conn.commit()
        conn.close()
    except Exception as e:
        return {"status": "error", "message": f"MySQL error: {str(e)}"}

    # Store to Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        for item in results:
            key = f"material:{item['title']}"
            r.hset(key, mapping={
                "title": item['title'],
                "description": item['description'],
                "source": item['source'],
                "url": item['url']
            })
    except Exception as e:
        return {"status": "error", "message": f"Redis error: {str(e)}"}

    return {"status": "success", "saved": len(results)}
