from django.contrib import admin
from .models import Grade, Course, Topic, Assessment, Student_Profile, Student_Progress,  School, Materials
from django.contrib.auth.models import User
from .models import PathFeedback, LearningGoal, LearningPath, TopicAssessmentResult 
from .models import Question, StudentAssessmentAttempt, AI_Assessment, Enrollment
admin.site.register(Grade)
admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(Assessment)
admin.site.register(Student_Profile)
admin.site.register(Materials)
admin.site.register(Student_Progress) 
admin.site.register(School)
admin.site.register(LearningGoal)
admin.site.register(LearningPath)
admin.site.register(PathFeedback)
admin.site.register(TopicAssessmentResult)
admin.site.register(Question)
admin.site.register(StudentAssessmentAttempt)
admin.site.register(AI_Assessment)
admin.site.register(Enrollment)
