from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



# Create your models here.
class Grade(models.Model):
    name = models.CharField(max_length=55)
    
    def __str__(self):
        return self.name
    
class Course(models.Model):
    title = models.CharField(max_length=65)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    description = models.TextField()
    def __str__(self):
        return self.title
class Topic(models.Model):
        name = models.CharField(max_length=55)
        course = models.ForeignKey(Course, on_delete=models.CASCADE)
        
        def __str__(self):
            return self.name
class Assessment(models.Model):
            course = models.ForeignKey(Course, on_delete=models.CASCADE)
            answer = models.TextField()
            topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
            question = models.TextField()
            def __str__(self):
                return self.name
class Student_Profile(models.Model):
      user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
      grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
      course = models.ForeignKey(Course, on_delete=models.CASCADE)
      def __str__(self):
          return self.user.username
class Materials(models.Model):
     MATERIAL_TYPE_CHOICES = [
         ('video', 'Video'),
         ('document', 'Document'),
         ('image', 'Image'),
         ('audio', 'Audio'),
     ]
     title = models.CharField(max_length=100)
     description = models.TextField()
     material_type = models.CharField(max_length=10, choices=MATERIAL_TYPE_CHOICES)
     file = models.FileField(upload_to='materials/')
     course = models.ForeignKey(Course, on_delete=models.CASCADE)
     topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
     def __str__(self):
         return self.title      
class Student_Progress(models.Model):
    student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    progress_percentage = models.FloatField(default=0.0)
    weak_areas = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course', 'topic')
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.title} - {self.topic.name}"                  
    
class Project(models.Model):
     title = models.CharField(max_length=100)
     description = models.TextField()
     course = models.ForeignKey(Course, on_delete=models.CASCADE)
     topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
     student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE)
     submission_date = models.DateTimeField(auto_now_add=True)
     def __str__(self):
         return self.title
class Quize(models.Model):
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    pass_score = models.FloatField(default=50.0)
    
    def __str__(self):
        return self.title
class Certificate(models.Model):
    student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    certificate_file = models.FileField(upload_to='certificates/')
    
    def __str__(self):
        return f"Certificate for {self.student.user.username} - {self.course.title}"
         