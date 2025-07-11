from django.shortcuts import render, redirect
from .models import Student_Profile, Course, Topic
from .scrapper import scrape_topic_data
from .learning_path import build_learning_path
from .Filter import filter_resources

def generate_learning_path_view(request):
    student = Student_Profile.objects.get(user=request.user)

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        course = Course.objects.get(id=course_id)
        weak_topic_ids = request.POST.getlist('weak_topics')
        weak_topics = Topic.objects.filter(id__in=weak_topic_ids, course=course)

        # Step 2: Scrape raw resources
        raw_scraped_data = scrape_topic_data([t.name for t in weak_topics])

        # Step 3: Filter & rank resources
        filtered_data = filter_resources(raw_scraped_data)

        # Step 4: Build learning path in DB
        build_learning_path(student, course, weak_topics, filtered_data)

        return redirect('student_profile')

    courses = Course.objects.all()
    return render(request, 'generate_learning_path.html', {'courses': courses})

