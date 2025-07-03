from django.shortcuts import render
from django.http import HttpResponse
from .models import Course, Topic, Assessment, Materials, Student_Profile, Student_Progress
from django.contrib.auth.decorators import login_required
from .forms import signupForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .mongo_service import store_learning_path, get_learning_path
from django.http import JsonResponse
from .redis_service import save_student_session, get_student_session
from .celery_tasks import generate_learning_path
from celery_tasks import generate_recommendations_task
from Filter import get_user_profile
from django.db import connection

username = "student123"
profile = get_user_profile(username)

if profile:
    generate_recommendations_task.delay(
        username,
        profile['interests'],
        profile['fav_sources']
    )


@login_required
def index(request):
    
    return render(request, 'index.html')
@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})
@login_required
def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    topics = Topic.objects.filter(course=course)
    materials = Materials.objects.filter(course=course)
    assessments = Assessment.objects.filter(course=course)
    return render(request, 'course_detail.html', {
        'course': course,
        'topics': topics,
        'materials': materials,
        'assessments': assessments
    })
@login_required
def topic_detail(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    materials = Materials.objects.filter(topic=topic)
    assessments = Assessment.objects.filter(topic=topic)
    return render(request, 'topic_detail.html', {
        'topic': topic,
        'materials': materials,
        'assessments': assessments
    })
def materials(request, material_id):
    topic = Topic.objects.get(id=material_id)
    materials = Materials.objects.filter(topic=topic)
    return render(request, 'materials.html', {'materials': materials, 'topic': topic})  


@login_required
def student_profile(request):
    student_profile = Student_Profile.objects.get(user=request.user)
    courses = Course.objects.filter(grade=student_profile.grade)
    progress = Student_Progress.objects.filter(student=student_profile)
    return render(request, 'student_profile.html', {
        'student_profile': student_profile,
        'courses': courses,
        'progress': progress
    })
@login_required
def student_progress(request):
    student_profile = Student_Profile.objects.get(user=request.user)
    progress = Student_Progress.objects.filter(student=student_profile)
    return render(request, 'student_progress.html', {
        'progress': progress,
        'student_profile': student_profile
    })
@login_required
def assessment_detail(request, assessment_id):
    course = Course.objects.get(assessment__id=assessment_id)
    topic = Topic.objects.get(assessment__id=assessment_id)
    question = Assessment.objects.get(id=assessment_id)
    return render(request, 'assessment_detail.html', {'assessment': question, 'course': course, 'topic': topic})
@login_required
def project(request):
    score = 0
    if request.method == 'POST':
        answers = request.POST.getlist('answers')
        assessment_id = request.POST.get('assessment_id')
        assessment = Assessment.objects.get(id=assessment_id)
        correct_answers = assessment.answer.split(',')
        
        for i, answer in enumerate(answers):
            if answer.strip().lower() == correct_answers[i].strip().lower():
                score += 1
        
        return render(request, 'assessment_result.html', {'score': score, 'total': len(correct_answers)})
    else:
        assessment_id = request.GET.get('assessment_id')
        assessment = Assessment.objects.get(id=assessment_id)
        return render(request, 'assessment.html', {'assessment': assessment})
@login_required
def Quiz_view(request):
    score = 0
    if request.method == 'POST':
        answers = request.POST.getlist('answers')
        assessment_id = request.POST.get('assessment_id')
        assessment = Assessment.objects.get(id=assessment_id)
        correct_answers = assessment.answer.split(',')
        
        for i, answer in enumerate(answers):
            if answer.strip().lower() == correct_answers[i].strip().lower():
                score += 1
        
        return render(request, 'quiz_result.html', {'score': score, 'total': len(correct_answers)})
    else:
        assessment_id = request.GET.get('assessment_id')
        assessment = Assessment.objects.get(id=assessment_id)
        return render(request, 'quiz.html', {'assessment': assessment})
@login_required
def certificate(request):
    student_profile = Student_Profile.objects.get(user=request.user)
    progress = Student_Progress.objects.filter(student=student_profile)
    completed_courses = [p.course for p in progress if p.completed]
    
    return render(request, 'certificate.html', {
        'student_profile': student_profile,
        'completed_courses': completed_courses
    })
def signup_view(request):
    if request.method == 'POST':
        form = signupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            student_profile = Student_Profile.objects.create(
                username=form.cleaned_data['username'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                school=form.cleaned_data['school'],
                grade=form.cleaned_data['grade'],
                course=form.cleaned_data['course']
            )
            return HttpResponse("Signup successful! Please log in.")
    else:
        form = signupForm()
    return render(request, 'signup.html', {'form': form})
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return HttpResponse("Invalid credentials")
    return render(request, 'login.html')    
def logout_view(request):
    logout(request)
    return redirect('index')  
def save_path(request):
    store_learning_path("stu001", ["Intro", "Loops", "Functions"])
    return JsonResponse({"status": "saved"})

def fetch_path(request):
    path = get_learning_path("stu001")
    return JsonResponse(path, safe=False)

def redis_save(request):
    save_student_session("stu001", "path=AI-Course")
    return JsonResponse({"status": "saved"})

def redis_get(request):
    data = get_student_session("stu001")
    return JsonResponse({"data": data.decode() if data else "not found"})
def start_path_generation(request):
    task = generate_learning_path.delay("stu001")
    return JsonResponse({"task_id": task.id})


def save_student_score(username, topic_id, score):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO student_assessments (username, topic_id, score)
            VALUES (%s, %s, %s)
        """, [username, topic_id, score])

