from django.test import TestCase

from django.http import JsonResponse
from .ai_grading import ai_grade_project
from .models import StudentProject

def test_grade_project(request, submission_id):
    submission = StudentProject.objects.get(id=submission_id)
    ai_grade_project(submission)
    return JsonResponse({
        "message": "Graded successfully",
        "grade": submission.grade,
        "feedback": submission.feedback
    })


# Create your tests here.
