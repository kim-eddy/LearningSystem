from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests

@csrf_exempt
def ai_grade_project(request):
    if request.method == 'POST':
        code = request.POST.get('code', '')
        title = request.POST.get('title', 'Untitled Project')
        if not code:
            return JsonResponse({'error': 'No code provided'}, status=400)

        # Send code to Gemini
        prompt = f"""
You're an expert teacher. Grade this student project titled "{title}":
{code}

Return format:
Grade: <grade>
Feedback: <feedback>
"""
        try:
            GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyAx4to8JSa0k9iuIALEky4S0WFIU1Z01xo"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = requests.post(GEMINI_API_URL, json=payload)
            response.raise_for_status()
            result = response.json()['candidates'][0]['content']['parts'][0]['text']

            lines = result.splitlines()
            grade = next((l.split(":", 1)[1].strip() for l in lines if "Grade:" in l), "N/A")
            feedback = next((l.split(":", 1)[1].strip() for l in lines if "Feedback:" in l), "N/A")

            return JsonResponse({'grade': grade, 'feedback': feedback})
        except Exception as e:
            return JsonResponse({'error': f"AI grading failed: {str(e)}"}, status=500)
