# smart_learning_assistant.py

from google import generativeai as genai
import mysql.connector
from pymongo import MongoClient
import redis
import json

# === 1. CONFIG ===
genai.configure(api_key="AIzaSyAmYRNOr1FakFQQaZ_zWRWAuZNcHRU3Vsk")
model = genai.GenerativeModel("gemini-2.5-flash")


# === 2. DATABASE FETCHERS ===

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


# === 3. FETCH STUDENT PROFILE ===

def get_user_profile(username):
    conn = mysql.connector.connect(
        host="localhost",
        user="emmanuel",
        password="K7154muhell",
        database="LearningSystem"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM student_profiles WHERE username = %s", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "username": result["username"],
            "interests": json.loads(result["interests"]),
            "fav_sources": json.loads(result["fav_sources"])
        }
    else:
        return None


# === 4. FORMATTER ===

def format_data_for_gemini(resources):
    formatted = ""
    for item in resources:
        formatted += f"\n📘 Title: {item.get('title')}\n📝 Description: {item.get('description')}\n🌍 Source: {item.get('source')}\n🔗 URL: {item.get('url')}\n---"
    return formatted


# === 5. GEMINI CALL ===

def call_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except json.JSONDecodeError:
        print(" Invalid JSON returned:\n", response.text)
        return {"error": "Invalid JSON returned by Gemini"}
    except Exception as e:
        return {"error": f"Gemini error: {str(e)}"}

# === 6. FILTER FUNCTION ===

def filter_resources(query):
    print(f"\n🔍 Filtering resources for: {query}")
    data = fetch_mysql_data() + fetch_mongo_data() + fetch_redis_data()
    formatted = format_data_for_gemini(data)

    prompt = f"""
A student searched for: "{query}"

Below is a list of learning materials. Return the 5 most relevant as a JSON list with title, description, source, and url.

Materials:
{formatted}
"""
    return call_gemini(prompt)


# === 7. RECOMMENDER FUNCTION ===

def recommend_resources(user_profile):
    print(f"\n🎁 Recommending for: {user_profile['username']} with interests: {', '.join(user_profile['interests'])}")
    data = fetch_mysql_data() + fetch_mongo_data() + fetch_redis_data()
    formatted = format_data_for_gemini(data)

    interests = ', '.join(user_profile['interests'])

    prompt = f"""
User '{user_profile['username']}' is interested in: {interests}

Below are learning resources. Based on their interests and preferred sources ({', '.join(user_profile['fav_sources'])}), recommend 5 materials in JSON format.

Materials:
{formatted}
"""
    return call_gemini(prompt)


# === 8. MAIN RUNNER ===

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
            print("Profile not found.")
            exit()

    else:
        print("Invalid choice")
        exit()

    # Output
    if "error" in results:
        print(f"\nError: {results['error']}")
    else:
        print("\n Results:")
        for res in results:
            print(f"📘 {res['title']} ({res['source']})\n🔗 {res['url']}\n📝 {res['description']}\n")
