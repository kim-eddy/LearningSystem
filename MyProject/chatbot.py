import requests
from django.conf import settings
GEMINI_API_KEY = settings.GEMINI_API_KEY

def gemini_chat(user_message):
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }

    response = requests.post(
        endpoint,
        params={"key": GEMINI_API_KEY},
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No reply.")
    else:
        return f"Error: {response.status_code}"
