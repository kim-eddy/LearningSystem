from django.shortcuts import render
from django.http import HttpResponse
from .models import Course, Topic, Assessment, Materials, Student_Profile, Student_Progress, AI_Assessment, LearningPath, Grade, School
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, StudentProfileUpdateForm, LanguagePreferenceForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from collections import defaultdict
from .models import ChatHistory
from .models import Project, StudentProject, TopicProgress
from .mongo_service import store_learning_path, get_learning_path
from django.http import JsonResponse
from .redis_service import save_student_session, get_student_session
from .celery_tasks import generate_recommendations_task
from django.utils import timezone
from django.views.decorators.http import require_POST   
from .models import TopicProgress, Student_Profile, Course, StudentBadge
from django.shortcuts import redirect
from django.db import connection
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .learning_path import build_learning_path
from .scrapper import scrape_topic_data
from .Filter import filter_resources
from .analyzer import analyze_student_performance
from django.views.decorators.csrf import csrf_exempt    
from pymongo import MongoClient 
import requests
import markdown
from .chatbot import gemini_chat
from django.utils.html import escape
from .ai_grading import ai_grade_project
from .Leaderboard_badges import award_badge
from .language_utils import get_translation, get_available_languages
from django.contrib import messages
import json
import os
import tempfile
import fitz
import logging
import google.generativeai as genai
from django.conf import settings    






logger = logging.getLogger(__name__)





user = None  # Placeholder for user object, to be used in views where needed


# Configure Gemini
genai.configure(api_key="AIzaSyAx4to8JSa0k9iuIALEky4S0WFIU1Z01xo")
model = genai.GenerativeModel("gemini-2.5-flash")

@csrf_exempt
@login_required
def gemini_chat_view(request):
    user = request.user
    if request.method == "POST":
        message = request.POST.get("message", "")
        uploaded_file = request.FILES.get("file")

        file_content = ""
        if uploaded_file:
            ext = uploaded_file.name.split(".")[-1].lower()
            temp_path = tempfile.mktemp(suffix=f".{ext}")
            with open(temp_path, "wb+") as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)

            try:
                if ext == "txt":
                    with open(temp_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                elif ext == "pdf":
                    doc = fitz.open(temp_path)
                    file_content = "\n".join(page.get_text() for page in doc)
                    doc.close()
                else:
                    file_content = "[Unsupported file format]"
            finally:
                os.remove(temp_path)

        # Combine file + message
        prompt = f"{file_content.strip()}\n\nUser's question: {message.strip()}" if file_content else message.strip()

        try:
            chat = model.start_chat(history=[])
            gemini_response = chat.send_message(prompt)
            response_text = gemini_response.text
        except Exception as e:
            response_text = f"Error: {str(e)}"

        ChatHistory.objects.create(
            user=user,
            message=message,
            gemini_response=response_text,
            timestamp=timezone.now()
        )
     

        return JsonResponse({"response": response_text})
    

# ============================================
# LANGUAGE PREFERENCE VIEWS
# ============================================

def select_language(request):
    """Display language selection during signup or first login"""
    user_language = 'en'
    if request.user.is_authenticated:
        try:
            profile = Student_Profile.objects.get(user=request.user)
            user_language = profile.preferred_language
        except Student_Profile.DoesNotExist:
            pass
    
    return render(request, 'language_selector.html', {
        'user_language': user_language,
        'languages': get_available_languages()
    })


@login_required
def set_language(request):
    """Set user's preferred language"""
    if request.method == 'POST':
        language = request.POST.get('language', 'en')
        
        try:
            profile = Student_Profile.objects.get(user=request.user)
            profile.preferred_language = language
            profile.save()
            messages.success(request, get_translation('language_updated', language))
        except Student_Profile.DoesNotExist:
            messages.error(request, 'Student profile not found.')
        
        return redirect('home')
    
    return redirect('language_settings')


@login_required
def language_settings(request):
    """User language preferences page"""
    try:
        profile = Student_Profile.objects.get(user=request.user)
    except Student_Profile.DoesNotExist:
        return redirect('select_language')
    
    if request.method == 'POST':
        form = LanguagePreferenceForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            language = form.cleaned_data.get('preferred_language', 'en')
            messages.success(request, get_translation('language_updated', language))
            return redirect('language_settings')
    else:
        form = LanguagePreferenceForm(instance=profile)
    
    return render(request, 'language_settings.html', {
        'form': form,
        'profile': profile,
        'languages': get_available_languages()
    })


def get_translation_json(request, key):
    """API endpoint to get translations"""
    try:
        profile = Student_Profile.objects.get(user=request.user) if request.user.is_authenticated else None
        language = profile.preferred_language if profile else 'en'
    except Student_Profile.DoesNotExist:
        language = 'en'
    
    translation = get_translation(key, language)
    return JsonResponse({'translation': translation, 'language': language})

def index(request):
    
    return render(request, 'index.html')

@login_required
def home(request):
    try:
        profile = Student_Profile.objects.get(user=request.user)
        language = profile.preferred_language
    except Student_Profile.DoesNotExist:
        language = 'en'
    
    context = {
        'user_language': language,
        'get_translation': lambda key: get_translation(key, language)
    }
    return render(request, 'home.html', context)

@login_required
def course_list(request):
    # Auto-create Student_Profile if it doesn't exist
    student_profile, created = Student_Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'grade': Grade.objects.first() or Grade.objects.create(name='Default Grade'),
            'school': School.objects.first() or School.objects.create(
                name='Default School',
                address='N/A',
                phone_number='N/A',
                email='default@school.com'
            )
        }
    )

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
            return redirect('/assessments/ai/')

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
    badges = StudentBadge.objects.filter(student=student_profile)
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
                user=request.user.id,
                interests=interests,
                
            )

            return redirect('student_profile')
    else:
        form = StudentProfileUpdateForm(instance=student_profile)

    return render(request, 'student_profile.html', {
        'student_profile': student_profile,
        'courses': courses,
        'progress': progress,
        'form': form,
        'badges': badges 
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
    course_title = course.title if course else "General"
    topics = Topic.objects.filter(course=course)

    if request.method == 'POST':
        # Evaluate answers
        # Fetch all AI_Assessment questions for this user/course/grade (all topics)
        ai_questions = AI_Assessment.objects.filter(
            user=user, course=course, grade_level=grade.id if hasattr(grade, 'id') else grade
        ).order_by('-created_at')
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

        # Advanced ordering: analyze and order topics
        # For AI assessments, analyze performance using ai_questions and user_answers
        # If your analyzer expects an object with .topic and .correct_answer, you can adapt it:
        topic_stats = {}
        for idx, q in enumerate(ai_questions):
            topic_id = q.topic.id if q.topic else None
            is_correct = (
                user_answers[idx]['selected'] and
                user_answers[idx]['selected'].strip().lower() == q.correct_answer.strip().lower()
            )
            if topic_id not in topic_stats:
                topic_stats[topic_id] = {'correct': 0, 'total': 0}
            topic_stats[topic_id]['total'] += 1
            if is_correct:
                topic_stats[topic_id]['correct'] += 1

        topic_scores = {}
        for topic_id, stats in topic_stats.items():
            topic_scores[topic_id] = stats['correct'] / stats['total'] if stats['total'] else 0.0

        all_topics = Topic.objects.filter(course=course)
        ordered_topics = sorted(
            all_topics,
            key=lambda t: topic_scores.get(t.id, 1)  # topics not assessed are treated as strongest (score=1)
        )

        scraped = scrape_topic_data([t.name for t in ordered_topics])
        filtered = filter_resources(scraped)
        build_learning_path(student_profile, course, ordered_topics, filtered)

        return redirect('learning_path_view')
    else:
        all_questions = []
        for topic in topics:
            topic_name = topic.name
            prompt = f"""
            You are an expert educational content generator. Create a 5-question multiple choice quiz for a grade {grade} student in the course '{course_title}' on the topic: '{topic_name}'.

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
                GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyAiLQuJFl5bNGDHJQIQoiwZN0r1Xnwzn1M"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                response = requests.post(GEMINI_API_URL, json=payload)
                response.raise_for_status()

                generated = response.json()['candidates'][0]['content']['parts'][0]['text']

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

                            all_questions.append({
                                "question": question_text,
                                "options": options,
                                "correct": correct_answer,
                                "course": course_title,
                                "topic": topic_name
                            })
                        else:
                            logger.warning(f"Skipping malformed line in Gemini output: {line}")
            except Exception as e:
                logger.error(f"Gemini API Error for topic {topic_name}: {e}")

        return render(request, 'assessment_detail.html', {
            'assessment': None,
            'auto_questions': all_questions,
            'grade': grade,
            'course': course,
            'topics': topics
        })

@login_required
def submit_assessment(request):
    score = 0
    if request.method == 'POST':
        answers = request.POST.getlist('answers')
        assessment_id = request.POST.get('assessment_id')
        assessment = get_object_or_404(Assessment, id=assessment_id)
        student = Student_Profile.objects.get(user=request.user)

        # Score
        correct_answers = assessment.answer.split(',')
        for i, answer in enumerate(answers):
            if answer.strip().lower() == correct_answers[i].strip().lower():
                score += 1

        
        

        topic_scores = analyze_student_performance(assessment, answers)  # {topic_id: percent}
        all_topics = Topic.objects.filter(course=assessment.course)
        ordered_topics = sorted(
            all_topics,
            key=lambda t: topic_scores.get(t.id, 0)  # topics with no score are treated as strongest
        )

        logger.info(f"Scraping topics: {[t.name for t in ordered_topics]}")

        scraped = scrape_topic_data([t.name for t in ordered_topics])
        filtered = filter_resources(scraped)
        build_learning_path(student, assessment.course, ordered_topics, filtered)

        return redirect('learning_path_view')  # or 'learning_resources'

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
            user.save()
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
    student = Student_Profile.objects.get(user=user)
    path_entries = LearningPath.objects.filter(student=student).order_by('order')
    learning_path = []

    # MongoDB setup
    from pymongo import MongoClient
    mongo_client = MongoClient("mongodb://mongo:OGjVByzPvFOpBaoejJuxWhZZnEwpUfxc@shortline.proxy.rlwy.net:57079")
    mongo_collection = mongo_client["LearningSystem"]["scraped_content"]

    for entry in path_entries:
        # Try to fetch resources from DB (MongoDB or other)
        resources = list(mongo_collection.find({
            "title": {"$regex": entry.topic.name, "$options": "i"},
            "user_id": user.id
        }))

        # Fallback to Gemini if no resources found
        if not resources:
            ai_resource = mongo_collection.find_one({
                "title": f"AI-generated: {entry.topic.name}",
                "user_id": user.id
            })
            if ai_resource:
                resources = [ai_resource]
            else:
                prompt = f"Provide a concise, student-friendly summary and a practical example for the topic '{entry.topic.name}' in the course '{entry.course.title}'."
                try:
                    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=AIzaSyAiLQuJFl5bNGDHJQIQoiwZN0r1Xnwzn1M"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    response = requests.post(GEMINI_API_URL, json=payload)
                    response.raise_for_status()
                    gemini_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    resource_doc = {
                        "title": f"AI-generated: {entry.topic.name}",
                        "url": " ",
                        "description": gemini_text,
                        "topic": entry.topic.name,
                        "course": entry.course.title,
                        "user_id": user.id
                    }
                    mongo_collection.insert_one(resource_doc)
                    resources = [resource_doc]
                except Exception as e:
                    resources = [{
                        "title": "No resources found",
                        "url": " ",
                        "description": f"Could not fetch content from Gemini: {e}"
                    }]

        # Convert markdown for this entry only
        for res in resources:
            try:
                res["description"] = markdown.markdown(res.get("description", ""))
            except Exception as e:
                logger.warning(f"Markdown conversion failed: {e}")
                res["description"] = "<p><em>Failed to load content.</em></p>"

        learning_path.append({
            "topic": entry.topic,      # Pass the Topic object
            "resources": resources
        })

    return render(request, 'learning_path.html', {"learning_path": learning_path})


@login_required
def learning_resources(request):
    user = request.user
    selected_course = request.GET.get('course')  # match the template
    selected_topic = request.GET.get('topic')    # needed for filtering

    # Connect to MongoDB
    client = MongoClient("mongodb://mongo:OGjVByzPvFOpBaoejJuxWhZZnEwpUfxc@shortline.proxy.rlwy.net:57079")
    db = client["LearningSystem"]
    collection = db["scraped_content"]

    # Get all resources for the logged-in user
    resources = list(collection.find({"user_id": int(user.id)}))

    # Group resources by course → topic
    grouped_resources = {}
    for res in resources:
        course = res.get("course", "Unknown Course")
        topic = res.get("topic", "Unknown Topic")
        grouped_resources.setdefault(course, {}).setdefault(topic, []).append(res)
    for res in resources:
        try:
            res["description"] = markdown.markdown(res.get("description", ""))
        except Exception as e:
            logger.warning(f"Markdown conversion failed: {e}")
            res["description"] = "<p><em>Failed to load content.</em></p>"
    
    return render(request, 'learning_resources.html', {
        "grouped_resources": grouped_resources,
        "selected_course": selected_course,     # pass to template
        "selected_topic": selected_topic        # pass to template
    })

def study_topic_view(request, topic_id):
    user = request.user
    topic = get_object_or_404(Topic, id=topic_id)

    # MongoDB connection
    client = MongoClient("mongodb://mongo:OGjVByzPvFOpBaoejJuxWhZZnEwpUfxc@shortline.proxy.rlwy.net:57079")
    db = client["LearningSystem"]
    collection = db["scraped_content"]

    # Try fetching existing resources
    resources = list(collection.find({
        "topic": topic.name,
        "user_id": int(user.id)
    }))

    # Fallback: scrape if no data found
    if not resources:
        scraped_data = scrape_topic_data([topic.name])
        if scraped_data:
            for item in scraped_data:
                item["user_id"] = int(user.id)
                collection.insert_one(item)
            resources = scraped_data
        else:
            resources = [{
                "title": "No resources found",
                "url": " ",
                "description": "No resources available for this topic."
            }]

    # Convert descriptions to HTML using markdown
    for res in resources:
        try:
            res["description"] = markdown.markdown(res.get("description", ""))
        except Exception as e:
            logger.warning(f"Markdown conversion failed: {e}")
            res["description"] = "<p><em>Failed to load content.</em></p>"
    for res in resources:
        try:
            res["description"] = markdown.markdown(res.get("description", ""))
        except Exception as e:
            logger.warning(f"Markdown conversion failed: {e}")
            res["description"] = "<p><em>Failed to load content.</em></p>"
    return render(request, "study_topic.html", {
        "topic": topic,
        "resources": resources
    })

@require_POST
def mark_topic_completed(request, topic_id):
    student = Student_Profile.objects.get(user=request.user)
    topic = Topic.objects.get(id=topic_id)
    

    progress, created = TopicProgress.objects.get_or_create(
        student=student,
        topic=topic,
        
    )
    progress.progress_percentage = 100.0
    progress.last_accessed = timezone.now()
    progress.save()
    update_course_progress(student, topic.course)
    return redirect('study_topic', topic_id=topic_id)


@csrf_exempt
def update_progress(request, topic_id):
    if request.method == 'POST':
        student = Student_Profile.objects.get(user=request.user)
        topic = Topic.objects.get(id=topic_id)

        progress, _ = TopicProgress.objects.get_or_create(student=student, topic=topic)
        progress.progress_percentage = min(progress.progress_percentage + 25.0, 100.0)
        progress.save()
        update_course_progress(student, topic.course)



        # If progress is now 100%, assign a project
        if progress.progress_percentage >= 100.0:
            # Assign a project for the course if not already assigned
            project = Project.objects.filter(course=topic.course).first()
            if project:
                StudentProject.objects.get_or_create(student=student, project=project)

        return JsonResponse({"progress": progress.progress_percentage})
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def project_view(request):
    student = Student_Profile.objects.get(user=request.user)
    enrolled_courses = student.enrolled_courses.all()

    # Get one project per course (or however many you prefer)
    projects = Project.objects.filter(course__in=enrolled_courses)

    student_projects = StudentProject.objects.filter(student=student)
    submitted_ids = [sp.project.id for sp in student_projects if sp.is_submitted]

    return render(request, 'project_assignment.html', {
        "projects": projects,
        "submitted_ids": submitted_ids
    })

@login_required
def submit_project(request, project_id):
    if request.method == 'POST':
        student = get_object_or_404(Student_Profile, user=request.user)
        project = get_object_or_404(Project, id=project_id)
        uploaded_file = request.FILES.get('project_file')

        if not uploaded_file:
            return HttpResponse("Please upload a file.", status=400)

        # Prevent duplicate submissions
        if StudentProject.objects.filter(student=student, project=project, is_submitted=True).exists():
            return HttpResponse("You have already submitted this project.", status=400)

        # Save submission
        student_project, created = StudentProject.objects.get_or_create(
            student=student,
            project=project
        )
        student_project.file = uploaded_file
        student_project.is_submitted = True
        student_project.save()

        #  Trigger AI grading
        ai_grade_project(student_project)

        return redirect('project_detail', project_id=project.id)

    return HttpResponse("Invalid request method.", status=405)
def update_course_progress(student, course):
    from .models import Topic, TopicProgress, Student_Progress

    all_topics = Topic.objects.filter(course=course)
    completed_topics = TopicProgress.objects.filter(
        student=student,
        topic__in=all_topics,  
        progress_percentage__gte=100.0
    ).count()

    total_topics = all_topics.count()
    percentage = round((completed_topics / total_topics) * 100.0, 2) if total_topics else 0.0

    # Handle duplicate Student_Progress entries (if any)
    student_progress_qs = Student_Progress.objects.filter(student=student, course=course)
    if student_progress_qs.count() > 1:
        # Keep the first, delete the rest
        first = student_progress_qs.first()
        student_progress_qs.exclude(id=first.id).delete()
        student_progress = first
    elif student_progress_qs.exists():
        student_progress = student_progress_qs.first()
    else:
        student_progress = Student_Progress(student=student, course=course)

    student_progress.progress_percentage = percentage
    student_progress.completed = (percentage == 100.0)
    student_progress.save()

def complete_topic(request, topic_id):
    # Your topic completion logic here
    ...
    # Trigger badge award
    award_badge.delay(request.user.id, "completed_first_topic")

def leaderboard_view(request):
    from .models import Leaderboard
    leaderboard = Leaderboard.objects.order_by('-score')[:10]  # Top 10 users
    return render(request, 'leaderboard.html', {'leaderboard': leaderboard})