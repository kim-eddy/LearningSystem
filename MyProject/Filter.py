from google import generativeai as genai
import mysql.connector
from pymongo import MongoClient
import redis
import json
import os
import django
import sys
from django.conf import settings
from MyProject.models import Student_Profile
from MyProject.models import Resources

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LearningSystem.settings")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()


genai.configure(api_key="settings.GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")




def fetch_mysql_data():
    conn = mysql.connector.connect(
        host="ballast.proxy.rlwy.net",
        port = '22356',
        user="root",
        password="JOwJHNqsuEITqzqJUNNVajFwaDPznwRO",
        database="railway",
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT title, description, url, topic_id FROM MyProject_resources")
    data = cursor.fetchall()
    conn.close()
    return data


def fetch_mongo_data():
    client = MongoClient("mongodb://mongo:OGjVByzPvFOpBaoejJuxWhZZnEwpUfxc@shortline.proxy.rlwy.net:57079")

    db = client["LearningSystem"]
    collection = db["resources"]
    results = collection.find({}, {"topic_id": 1, "title": 1, "description": 1,  "url": 1})
    return list(results)


def fetch_redis_data():
    r = redis.Redis("redis://default:LKIQbWKQHXlHIcrNAXAhJBGPGjSCuXAf@mainline.proxy.rlwy.net:11017")
    keys = r.keys("material:*")
    results = []
    for key in keys:
        item = r.hgetall(key)
        decoded_item = {k.decode(): v.decode() for k, v in item.items()}
        results.append(decoded_item)
    return results




def get_user_profile(user):
    conn = mysql.connector.connect(
        host="ballast.proxy.rlwy.net",
        user="root",
        password="JOwJHNqsuEITqzqJUNNVajFwaDPznwRO",
        database="railway"
    )
    cursor = conn.cursor(dictionary=True)

    # user is a Django User object; get profile by user.id
    cursor.execute("SELECT * FROM MyProject_student_profile WHERE user_id = %s", (user.id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return None

    cursor.execute("""
        SELECT topic_id FROM MyProject_student_assessment
        WHERE username = %s AND score < 50
    """, (user.username,))
    weak_topics = [row['topic_id'] for row in cursor.fetchall()]

    conn.close()

    return {
        "username": user.username,
        "interests": json.loads(result["interests"]),
        "weak_topics": weak_topics
    }





def format_data_for_gemini(resources):
    formatted = ""
    for item in resources:
        formatted += f"\n Title: {item.get('title')}\n Description: {item.get('description')}\n  URL: {item.get('url')}\n topic_id:{item.get('topic_id')}\n"
    return formatted




def call_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]  
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]  

        return json.loads(raw_text)

    except json.JSONDecodeError:
        print(" Invalid JSON returned:\n", response.text)
        return {"error": "Invalid JSON returned by Gemini"}
    except Exception as e:
        return {"error": f"Gemini error: {str(e)}"}



def filter_resources(query):
    print(f"\n Filtering resources for: {query}")
    data = fetch_mysql_data() + fetch_mongo_data() + fetch_redis_data()
    formatted = format_data_for_gemini(data)

    prompt = f"""
A student searched for: "{query}"

Below is a list of learning materials. Return the 5 most relevant as a JSON list with title, description, source, and url.

Materials:
{formatted}
"""
    results = call_gemini(prompt)

    if isinstance(results, list):
        
        try:
            conn = mysql.connector.connect(
                host="ballast.proxy.rlwy.net",
                user="root",
                password="JOwJHNqsuEITqzqJUNNVajFwaDPznwRO",
                database="railway"
            )
            cursor = conn.cursor()
            for item in results:
                cursor.execute("""
                    INSERT INTO MyProject_resources (title, description, source, url, topic_id)
                    VALUES (%s, %s, %s, %s)
                """, (item['title'], item['description'], item['url'], item['topic_id']))
            conn.commit()
            conn.close()
            print(" Saved filtered results to MySQL")
        except Exception as e:
            print(f" MySQL Save Error: {e}")

        
        try:
            r = redis.Redis("redis://default:LKIQbWKQHXlHIcrNAXAhJBGPGjSCuXAf@mainline.proxy.rlwy.net:11017")
            for item in results:
                key = f"material:{item['title']}"
                r.hset(key, mapping={
                    "title": item['title'],
                    "description": item['description'],
                    
                    "url": item['url'],
                    
                })
            print(" Cached filtered results in Redis")
        except Exception as e:
            print(f" Redis Save Error: {e}")

    return results





def recommend_resources(user):
    user_profile = get_user_profile(user)
    if not user_profile:
        print("No user profile found.")
        return {"error": "No user profile found."}

    print(f"\n Recommending for: {user.username} with interests: {', '.join(user_profile['interests'])}")


    all_data = fetch_mysql_data() + fetch_mongo_data() + fetch_redis_data()
    filtered_data = [
        item for item in all_data 
        if 'topic_id' in item and str(item['topic_id']) in map(str, user_profile['weak_topics'])
    ]


    # If no filtered data, let Gemini generate new materials based on interests and fav_sources
    if not filtered_data:
        print("No relevant materials found for the student's weak topics. Using Gemini to generate new materials based on interests and sources.")
        interests = ', '.join(user_profile['interests'])
        prompt = f"""
User '{user.username}' is interested in: {interests}.
Generate 5 new learning materials (not from a provided list) as a JSON list. Each item should have title, description, source, and url. Base your recommendations on the user's interests and preferred sources: {', '.join(user_profile.get('fav_sources', []))}.
"""
    else:
        formatted = format_data_for_gemini(filtered_data)
        interests = ', '.join(user_profile['interests'])
        prompt = f"""
User '{user.username}' is interested in: {interests}

Below are learning resources. Based on their interests and preferred sources ({', '.join(user_profile.get('fav_sources', []))}), recommend 5 materials in JSON format.

Materials:
{formatted}
"""

    results = call_gemini(prompt)

    if isinstance(results, list):
        # Save to MySQL (deduplicated)
        try:
            conn = mysql.connector.connect(
                host="ballast.proxy.rlwy.net",
                user="root",
                password="JOwJHNqsuEITqzqJUNNVajFwaDPznwRO",
                database="railway"
            )
            cursor = conn.cursor()
            for item in results:
                cursor.execute("SELECT COUNT(*) FROM MyProject_resources WHERE title = %s AND url = %s", (item['title'], item['url']))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO MyProject_resources (title, description, url, topic_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (item['title'], item['description'], item['url'], item['topic_id']))
            conn.commit()
            conn.close()
            print("  Saved to MySQL (deduplicated)")
        except Exception as e:
            print(f"  MySQL Save Error: {e}")

        # Save to MongoDB
        try:
            client = MongoClient("mongodb://mongo:OGjVByzPvFOpBaoejJuxWhZZnEwpUfxc@shortline.proxy.rlwy.net:57079")
            db = client["LearningSystem"]
            collection = db["recommended_materials"]
            for item in results:
                item_with_user = dict(item)
                item_with_user["username"] = user.username
                collection.insert_one(item_with_user)
            print("  Saved recommended results to MongoDB")
        except Exception as e:
            print(f"  MongoDB Save Error: {e}")

        # Save to Redis (deduplicated)
        try:
            r = redis.Redis("redis://default:LKIQbWKQHXlHIcrNAXAhJBGPGjSCuXAf@mainline.proxy.rlwy.net:11017")
            for item in results:
                key = f"material:{item['title']}"
                if not r.exists(key):
                    r.hset(key, mapping={
                        "title": item['title'],
                        "description": item['description'],
                        "source": item['source'],
                        "url": item['url'],
                        
                    })
            print("  Cached in Redis (deduplicated)")
        except Exception as e:
            print(f"  Redis Save Error: {e}")
    else:
        print("  Gemini returned error or invalid response. Skipping database storage.")

    return results




if __name__ == "__main__":
    print("=== Smart Learning Assistant ===\n")

    mode = input("Choose mode: (1) Filter (2) Recommend → ")

    if mode == "1":
        user_query = input("Enter student query: ")
        results = filter_resources(user_query)

    elif mode == "2":
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = input("Enter student username: ")
        try:
            user = User.objects.get(username=username)
        except Exception:
            print("User not found.")
            exit()
        results = recommend_resources(user)
    else:
        print(" Invalid choice")
        exit()

    if isinstance(results, dict) and "error" in results:
        print(f"\n Error: {results['error']}")
    else:
        print("\n Recommended Results:")
        for res in results:
            print(f"  {res['title']} ({res['source']})")
            print(f" {res['url']}\n  {res['description']}\n")
