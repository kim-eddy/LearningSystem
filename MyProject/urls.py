from django.urls import path
from .generate_learning_path import generate_learning_path_view
from .ai_grading import ai_grade_project
from .tests import test_grade_project

from .views import (
    index,
    home,
    course_list,
    course_detail,
    topic_detail,
    student_profile,
    student_progress,
    assessment_detail,
    submit_assessment,
    materials_view,
    signup_view,
    save_path,
    fetch_path,
    redis_get,
    redis_save,
    Quiz_view,
    learning_resources,
    learning_path_view,
    study_topic_view,
    mark_topic_completed,
    update_progress,
    project_view,
    gemini_chat_view,
    leaderboard_view
)
urlpatterns = [
    path('', index, name='index'),
    path('home/', home, name='home'),
    path('courses/', course_list, name='course_list'),
    path('courses/<int:course_id>/', course_detail, name='course_detail'),
    path('topics/<int:topic_id>/', topic_detail, name='topic_detail'),
    path('student/profile/', student_profile, name='student_profile'),
    path('student/progress/', student_progress, name='student_progress'),
    path('assessments/<int:assessment_id>/', assessment_detail, name='assessment_detail'),
    path('assessments/ai/', assessment_detail, name='ai_assessment'),
    path('submit_assessment/', submit_assessment, name='submit_assessment'),
    path('materials_view/<int:material_id>/', materials_view, name='materials_view'),
    path('signup/', signup_view, name='signup'),
    path('save-path/', save_path,name='save_path'),
    path('fetch-path/', fetch_path,name='fetch_path'),
    path('redis/get/', redis_get),
    path('redis/save/', redis_save),
    path('quiz/', Quiz_view, name='quiz'),
    path('learning-resources/', learning_resources, name='learning_resources'),
    path('generate-learning-path/', generate_learning_path_view, name='generate_learning_path'),
    path('learning-path/', learning_path_view, name='learning_path_view'),
    path('study-topic/<int:topic_id>/', study_topic_view, name='study_topic'),
    path('study-topic/<int:topic_id>/progress/', update_progress, name='update_progress'),
    path('study-topic/<int:topic_id>/resources/', study_topic_view, name='study_topic_resources'),
    path('study/topic/<int:topic_id>/complete/', mark_topic_completed, name='mark_topic_completed'),
    path('project/<int:project_id>/', project_view, name='project_view'),
    path('test/grade/<int:submission_id>/', test_grade_project, name='test_grade_project'),
    path('gemini-chat/', gemini_chat_view, name='gemini_chat'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),



]