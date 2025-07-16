from django.contrib import admin
from .models import Grade, Course, Topic, Assessment, Student_Profile, Student_Progress,  School, Materials
from django.contrib.auth.models import User
from .models import PathFeedback, LearningGoal, LearningPath, TopicAssessmentResult 
from .models import Question, StudentAssessmentAttempt, AI_Assessment, Enrollment, Project, StudentProject, ChatHistory
from .models import StudentBadge, Badges, Leaderboard
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
admin.site.register(Project)
admin.site.register(StudentProject)
admin.site.register(ChatHistory)
admin.site.register(StudentBadge)
admin.site.register(Badges)
admin.site.register(Leaderboard)
