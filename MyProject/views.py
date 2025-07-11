from django.shortcuts import render
from django.http import HttpResponse
from .models import Course, Topic, Assessment, Materials, Student_Profile, Student_Progress, AI_Assessment
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, StudentProfileUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .mongo_service import store_learning_path, get_learning_path
from django.http import JsonResponse
from .redis_service import save_student_session, get_student_session
from .celery_tasks import generate_recommendations_task
from .Filter import get_user_profile
from django.db import connection
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .learning_path import build_learning_path
from .scrapper import scrape_topic_data
from .Filter import filter_resources
from .analyzer import analyze_student_performance
from pymongo import MongoClient 
import requests

import logging

logger = logging.getLogger(__name__)






user = None  # Placeholder for user object, to be used in views where needed


@login_required
def index(request):
    
    return render(request, 'index.html')

@login_required
def course_list(request):
    student_profile = get_object_or_404(Student_Profile, user=request.user)

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        already_enrolled = Student_Progress.objects.filter(
            student=student_profile, course=course
        ).exists()

        if not already_enrolled:
            Student_Progress.objects.create(
                student=student_profile,
                course=course,
                topic=None
            )
        assessment = Assessment.objects.filter(course=course).first()

        if assessment:
            return redirect('assessment_detail', assessment_id=assessment.id)
        else:
            # No manual assessment exists, redirect to AI assessment (no assessment_id)
            ai_url = '/assessments/ai/'  
            return redirect(ai_url)

    courses = Course.objects.all()
    return render(request, 'course_list.html', {
        'courses': courses,
        'student_profile': student_profile
    })

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
def materials_view(request, material_id):
    topic = Topic.objects.get(id=material_id)
    materials = Materials.objects.filter(topic=topic)
    return render(request, 'materials.html', {'materials': materials, 'topic': topic})  


@login_required
def student_profile(request):
    student_profile = Student_Profile.objects.get(user=request.user)
    courses = Course.objects.filter(grade=student_profile.grade)
    progress = Student_Progress.objects.filter(student=student_profile)
    interests = request.POST.get('interests', '')
    student_profile.save()

    if request.method == 'POST':
        form = StudentProfileUpdateForm(request.POST, instance=student_profile)
        if form.is_valid():
            form.save()

            # Trigger AI recommendations using updated interests and current course
            interests = form.cleaned_data.get('interests', [])
            course_title = courses.first().title if courses.exists() else "General"

            generate_recommendations_task.delay(
                user=request.user,
                interests=interests,
                fav_sources=[course_title]
            )

            return redirect('student_profile')
    else:
        form = StudentProfileUpdateForm(instance=student_profile)

    return render(request, 'student_profile.html', {
        'student_profile': student_profile,
        'courses': courses,
        'progress': progress,
        'form': form  
    })
@login_required
def student_progress(request):
    student_profile = Student_Profile.objects.get(user=request.user)
    progress = Student_Progress.objects.filter(student=student_profile)
    
    selected_course_id = request.GET.get('course')

    if selected_course_id:
        progress = Student_Progress.objects.filter(student=student_profile, course__id=selected_course_id)
    else:
        progress = Student_Progress.objects.filter(student=student_profile)

    courses = Course.objects.filter(grade=student_profile.grade)
    return render(request, 'student_progress.html', {
        'progress': progress,
        'student_profile': student_profile,
        'courses': courses,
        'selected_course_id': int(selected_course_id) if selected_course_id else None
    })

@login_required
def assessment_detail(request, assessment_id=None):
    user = request.user

    if assessment_id:
        assessment = get_object_or_404(AI_Assessment, id=assessment_id, user=user)
        return render(request, 'assessment_detail.html', {
            'assessment': assessment,
            'course': assessment.course,
            'topic': assessment.topic
        })

    # GET: Generate and show quiz, POST: Evaluate answers
    student_profile = Student_Profile.objects.get(user=user)
    grade = student_profile.grade
    enrolled_progress = Student_Progress.objects.filter(student=student_profile, completed=False).order_by('-id').first()
    if enrolled_progress:
        course = enrolled_progress.course
    else:
        course = Course.objects.filter(grade=grade).first()
    topic = Topic.objects.filter(course=course).first() if course else None
    course_title = course.title if course else "General"
    topic_name = topic.name if topic else "General"

    if request.method == 'POST':
        # Evaluate answers
        # Fetch the latest 5 AI_Assessment questions for this user/course/topic/grade
        ai_questions = AI_Assessment.objects.filter(user=user, course=course, topic=topic, grade_level=grade.id if hasattr(grade, 'id') else grade).order_by('-created_at')[:5][::-1]
        user_answers = []
        score = 0
        total = len(ai_questions)
        for idx, q in enumerate(ai_questions):
            ans = request.POST.get(f'answers_{idx}')
            user_answers.append({'question': q.question, 'selected': ans, 'correct': q.correct_answer})
            # Save selected answer
            q.selected_answer = ans
            q.save()
            if ans and ans.strip() == q.correct_answer.strip():
                score += 1
        percentage = round((score / total) * 100, 2) if total else 0
        return render(request, 'quiz_result.html', {
            'score': score,
            'total': total,
            'percentage': percentage,
            'user_answers': user_answers,
            'course': course,
            'topic': topic
        })
    else:
        # Generate new quiz
        prompt = f"""
        You are an expert educational content generator. Create a 5-question multiple choice quiz for a grade {grade} student in the course '{course_title}' on the topic: '{topic_name if topic else 'any relevant topic'}'.

        For each question, strictly use the following format (one line per question):
        question|option1,option2,option3,option4|correct_option

        - Each question must have exactly 4 options, separated by commas.
        - The correct_option must exactly match one of the options.
        - Do not number the questions or add any extra text or explanation.
        - Only output the 5 lines, one for each question, in the format above.
        - Example:
        What is 2+2?|3,4,5,6|4
        ...
        """
        try:
            GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyAmYRNOr1FakFQQaZ_zWRWAuZNcHRU3Vsk"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = requests.post(GEMINI_API_URL, json=payload)
            response.raise_for_status()

            generated = response.json()['candidates'][0]['content']['parts'][0]['text']

            questions = []
            for line in generated.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) == 3:
                        q, opts, correct = parts
                        options = [o.strip() for o in opts.split(',')]
                        question_text = q.strip()
                        correct_answer = correct.strip()

                        # Save to DB
                        AI_Assessment.objects.create(
                            user=user,
                            course=course,
                            topic=topic,
                            question=question_text,
                            options=options,
                            correct_answer=correct_answer,
                            grade_level=grade.id if hasattr(grade, 'id') else grade,
                        )

                        questions.append({
                            "question": question_text,
                            "options": options,
                            "correct": correct_answer,
                            "course": course_title,
                            "topic": topic_name
                        })
                    else:
                        logger.warning(f"Skipping malformed line in Gemini output: {line}")

            return render(request, 'assessment_detail.html', {
                'assessment': None,
                'auto_questions': questions,
                'grade': grade,
                'course': course,
                'topic': topic
            })
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API Error: {e}")
            return HttpResponse(f"Gemini API failed: {str(e)}", status=500)
        except KeyError as e:
            logger.error(f"Gemini parsing error: {e}")
            return HttpResponse("Failed to parse Gemini response.", status=500)

@login_required
def project(request):
    score = 0
    if request.method == 'POST':
        answers = request.POST.getlist('answers')
        assessment_id = request.POST.get('assessment_id')
        assessment = get_object_or_404(Assessment, id=assessment_id)
        student = Student_Profile.objects.get(user=request.user)

        # Step 1: Score
        correct_answers = assessment.answer.split(',')
        for i, answer in enumerate(answers):
            if answer.strip().lower() == correct_answers[i].strip().lower():
                score += 1

        
        

        weak_topic_ids = analyze_student_performance(assessment, answers)
        weak_topics = Topic.objects.filter(id__in=weak_topic_ids)

        logger.info(f"Scraping topics: {[t.name for t in weak_topics]}")

        # Step 3: Scrape & Filter
        scraped = scrape_topic_data([t.name for t in weak_topics])
        filtered = filter_resources(scraped)

        logger.info(f"Filtered data: {filter_resources}")


        # Step 4: Build Path
        build_learning_path(student, assessment.course, weak_topics, filtered)

        return render(request, 'assessment_result.html', {
            'score': score,
            'total': len(correct_answers),
            'percentage': round((score / len(correct_answers)) * 100, 2)
        })

    else:
        assessment_id = request.GET.get('assessment_id')
        assessment = get_object_or_404(Assessment, id=assessment_id)
        return render(request, 'assessment.html', {'assessment': assessment})

@login_required
def Quiz_view(request):
    if request.method == 'POST':
        score = 0
        assessment_id = request.POST.get('assessment_id')
        answers = request.POST.getlist('answers')

        assessment = get_object_or_404(Assessment, id=assessment_id)
        correct_answers = assessment.answer.split(',')

        if len(answers) != len(correct_answers):
            return HttpResponse("Mismatch in number of answers submitted.")

        for i, answer in enumerate(answers):
            if answer.strip().lower() == correct_answers[i].strip().lower():
                score += 1

        total = len(correct_answers)
        percentage = round((score / total) * 100, 2)

        # Save student progress
        topic = assessment.topic
        student = Student_Profile.objects.get(user=request.user)
        Student_Progress.objects.update_or_create(
            student=student,
            course=assessment.course,
            topic=topic,
            defaults={
                'completed': percentage >= 60,
                'progress_percentage': percentage,
                'weak_areas': '' if percentage >= 60 else topic.name
            }
        )

        # Optionally regenerate learning path if score is low
        if percentage < 60:
            from .celery_tasks import regenerate_learning_path_task
            regenerate_learning_path_task.delay(request.user.username, topic.id)

        return render(request, 'quiz_result.html', {
            'score': score,
            'total': total,
            'percentage': percentage
        })

    else:
        assessment_id = request.GET.get('assessment_id')
        assessment = get_object_or_404(Assessment, id=assessment_id)
        questions = assessment.question.split('|')
        return render(request, 'quiz.html', {
            'assessment': assessment,
            'questions': questions
        })

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
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password'],  
            )

            student_profile = Student_Profile.objects.create(
                user=user,
                phone_number=form.cleaned_data['phone_number'],
                school=form.cleaned_data['school'],  
                grade=form.cleaned_data['grade']
            )

            return redirect('login')
    else:
        form = SignupForm()
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
    store_learning_path(request.user, ["Intro", "Loops", "Functions"])
    return JsonResponse({"status": "saved"})


def fetch_path(request):
    path = get_learning_path(request.user)
    return JsonResponse(path, safe=False)


def redis_save(request):
    save_student_session(request.user, "path=AI-Course")
    return JsonResponse({"status": "saved"})


def redis_get(request):
    data = get_student_session(request.user)
    return JsonResponse({"data": data.decode() if data else "not found"})


def save_student_score(user, topic_id, score):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO student_assessments (user_id, topic_id, score)
            VALUES (%s, %s, %s)
        """, [user.id, topic_id, score])


@login_required
def learning_path_view(request):
    user = request.user
    path = get_learning_path(user)

    if not path:
        return HttpResponse("No personalized learning path found yet.")

    return render(request, 'learning_path.html', {
        'learning_path': path
    })



@login_required
def learning_resources(request):
    user = request.user

    # Connect to MongoDB
    client = MongoClient("mongodb://emmanuel:K7154muhell@localhost:27017/?authSource=admin")
    db = client["LearningSystem"]
    collection = db["scraped_content"]  

    # Ensure type matches what was stored
    resources = list(collection.find({"user_id": int(user.id)}))

    return render(request, 'learning_resources.html', {
        "resources": resources
    })