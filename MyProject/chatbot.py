import requests
from django.conf import settings
# Assuming GEMINI_API_KEY is defined in settings
GEMINI_API_KEY = settings.GEMINI_API_KEY 

def gemini_chat(user_message):
    # 1. FIX: Use a properly formatted f-string or simple string for the endpoint URL.
    # The API key should be passed as a parameter, not embedded in the base URL string.
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }

    response = requests.post(
        endpoint,
        # 2. FIX: The API key is correctly passed here as a query parameter.
        params={"key": GEMINI_API_KEY},
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        # 3. IMPROVEMENT: Use .get() defensively for safer parsing of the JSON response.
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (IndexError, KeyError):
            return "Error: Could not parse Gemini response."
    else:
        # Include the response text for better debugging
        return f"Error: {response.status_code} - {response.text}"