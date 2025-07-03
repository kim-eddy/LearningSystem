from google import generativeai as genai
import mysql.connector
from pymongo import MongoClient
import redis
import json


genai.configure(api_key="AIzaSyAmYRNOr1FakFQQaZ_zWRWAuZNcHRU3Vsk")
model = genai.GenerativeModel("gemini-2.5-flash")




def fetch_mysql_data():
    conn = mysql.connector.connect(
        host="localhost",
        port = '3306',
        user="emmanuel",
        password="K7154muhell",
        database="LearningSystem",
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT title, description, source, url FROM resources")
    data = cursor.fetchall()
    conn.close()
    return data


def fetch_mongo_data():
    client = MongoClient("mongodb://emmanuel:K7154muhell@localhost:27017/?authSource=admin")

    db = client["LearningSystem"]
    collection = db["resources"]
    results = collection.find({}, {"_id": 0, "title": 1, "description": 1, "source": 1, "url": 1})
    return list(results)


def fetch_redis_data():
    r = redis.Redis(host='localhost', port=6379, db=0)
    keys = r.keys("material:*")
    results = []
    for key in keys:
        item = r.hgetall(key)
        decoded_item = {k.decode(): v.decode() for k, v in item.items()}
        results.append(decoded_item)
    return results




def get_user_profile(username):
    conn = mysql.connector.connect(
        host="localhost",
        user="emmanuel",
        password="K7154muhell",
        database="LearningSystem"
    )
    cursor = conn.cursor(dictionary=True)

    
    cursor.execute("SELECT * FROM MyProject_student_profile WHERE username = %s", (username,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        return None

    
    cursor.execute("""
        SELECT topic_id FROM student_assessment
        WHERE username = %s AND score < 50
    """, (username,))
    weak_topics = [row['topic_id'] for row in cursor.fetchall()]

    conn.close()

    return {
        "username": result["username"],
        "interests": json.loads(result["interests"]),
        "fav_sources": json.loads(result["fav_sources"]),
        "weak_topics": weak_topics
    }





def format_data_for_gemini(resources):
    formatted = ""
    for item in resources:
        formatted += f"\n Title: {item.get('title')}\n Description: {item.get('description')}\n🌍 Source: {item.get('source')}\n🔗 URL: {item.get('url')}\n---"
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
            print(" Saved filtered results to MySQL")
        except Exception as e:
            print(f" MySQL Save Error: {e}")

        
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
            print(" Cached filtered results in Redis")
        except Exception as e:
            print(f" Redis Save Error: {e}")

    return results




def recommend_resources(user_profile):
    print(f"\n Recommending for: {user_profile['username']} with interests: {', '.join(user_profile['interests'])}")

    
    all_data = fetch_mysql_data() + fetch_mongo_data() + fetch_redis_data()
    
    filtered_data = [
        item for item in all_data 
        if 'topic_id' in item and str(item['topic_id']) in map(str, user_profile['weak_topics'])
    ]

    if not filtered_data:
        print(" No relevant materials found for the student's weak topics.")
        return {"error": "No materials to recommend."}

    
    formatted = format_data_for_gemini(filtered_data)
    interests = ', '.join(user_profile['interests'])

    prompt = f"""
User '{user_profile['username']}' is interested in: {interests}

Below are learning resources. Based on their interests and preferred sources ({', '.join(user_profile['fav_sources'])}), recommend 5 materials in JSON format.

Materials:
{formatted}
"""

    
    results = call_gemini(prompt)

    
    if isinstance(results, list):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="emmanuel",
                password="K7154muhell",
                database="LearningSystem"
            )
            cursor = conn.cursor()

            for item in results:
                cursor.execute("SELECT COUNT(*) FROM resources WHERE title = %s AND url = %s", (item['title'], item['url']))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO resources (title, description, source, url)
                        VALUES (%s, %s, %s, %s)
                    """, (item['title'], item['description'], item['source'], item['url']))
            conn.commit()
            conn.close()
            print("  Saved to MySQL (deduplicated)")
        except Exception as e:
            print(f"  MySQL Save Error: {e}")

        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            for item in results:
                key = f"material:{item['title']}"
                if not r.exists(key):
                    r.hset(key, mapping={
                        "title": item['title'],
                        "description": item['description'],
                        "source": item['source'],
                        "url": item['url']
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
        username = input("Enter student username: ")
        user_profile = get_user_profile(username)

        if user_profile:
            results = recommend_resources(user_profile)
        else:
            print(" Profile not found.")
            exit()
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
