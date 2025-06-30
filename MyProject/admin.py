from django.contrib import admin
from .models import Grade, Course, Topic, Assessment, Student_Profile, Student_Progress, Student, School, Materials
from django.contrib.auth.models import User

admin.site.register(Grade)
admin.site.register(Course)
admin.site.register(Topic)
admin.site.register(Assessment)
admin.site.register(Student_Profile)
admin.site.register(Materials)
admin.site.register(Student_Progress) 
admin.site.register(Student)  
admin.site.register(School)
  
# Register your models here.
