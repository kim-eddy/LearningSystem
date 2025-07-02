from django.urls import path
from .views import (
    index,
    course_list,
    course_detail,
    topic_detail,
    student_profile,
    student_progress,
    assessment_detail,
    project,
    materials,
    signup_view,
    save_path,
    fetch_path,
    redis_get,
    redis_save,       
)
urlpatterns = [
    path('', index, name='index'),
    path('courses/', course_list, name='course_list'),
    path('courses/<int:course_id>/', course_detail, name='course_detail'),
    path('topics/<int:topic_id>/', topic_detail, name='topic_detail'),
    path('student/profile/', student_profile, name='student_profile'),
    path('student/progress/', student_progress, name='student_progress'),
    path('assessments/<int:assessment_id>/', assessment_detail, name='assessment_detail'),
    path('project/', project, name='project'),
    path('materials/<int:material_id>/', materials, name='materials'),
    path('signup/', signup_view, name='signup'),
    path('save-path/', save_path,name='save_path'),
    path('fetch-path/', fetch_path,name='fetch_path'),
    path('redis/get/', redis_get),
    path('redis/save/', redis_save),
    

]