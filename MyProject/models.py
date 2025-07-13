from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

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
    question = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    answer = models.TextField()

    def __str__(self):
        return f"Assessment on {self.topic.name}"


class Student_Profile(models.Model):
      user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
      grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
      courses = models.ManyToManyField(Course, blank=True)
      school = models.ForeignKey('School', on_delete=models.CASCADE, blank=True, null=True)
      phone_number = models.CharField(max_length=15, blank=True)
      email = models.EmailField(blank=True)
      interests = models.JSONField(default=list, blank=True)  
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
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    progress_percentage = models.FloatField(default=0.0)
    weak_areas = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course.title}" + (f" - {self.topic.name}" if self.topic else "")

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
    question = models.TextField(default="Sample question")
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
class School(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    subscription_plan = models.CharField(max_length=50, choices=[
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ], default='free')
    subscribed_on = models.DateTimeField(auto_now_add=True)
    subscription_active = models.BooleanField(default=True)
    subscription_expiry = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.name
     
class LearningGoal(models.Model):
    student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.title}"

class LearningPath(models.Model):
    goal = models.ForeignKey(LearningGoal, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    order = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
        default='not_started'
    )
    recommended_by_ai = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        unique_together = ('goal', 'topic')

    def __str__(self):
        return f"{self.goal.title} - {self.topic.name}"
class TopicAssessmentResult(models.Model):
    student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.FloatField()
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.topic.name} - {self.score}"

class PathFeedback(models.Model):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    feedback = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

class LearningPathTopic(models.Model):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    order = models.IntegerField()

class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True)
    question_text = models.TextField()
    options = models.JSONField()  # List of strings
    correct_answer = models.CharField(max_length=255)

class StudentAssessmentAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.CharField(max_length=50)
    questions = models.ManyToManyField(Question)
    submitted = models.BooleanField(default=False)
    score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AI_Assessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    question = models.TextField()
    options = models.JSONField(help_text="List of options in JSON format")
    correct_answer = models.CharField(max_length=255)
    selected_answer = models.CharField(max_length=255, null=True, blank=True)
    is_correct = models.BooleanField(null=True)
    generated_by_ai = models.BooleanField(default=True)
    grade_level = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.selected_answer:
            self.is_correct = (self.selected_answer == self.correct_answer)
        super().save(*args, **kwargs)     

class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True) 

class TopicProgress(models.Model):
    student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    progress_percentage = models.FloatField(default=0.0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'topic')

    def __str__(self):
        return f"{self.student.user.username} - {self.topic.name} - {self.progress_percentage}%"      
    

class StudentProject(models.Model):
    student = models.ForeignKey(Student_Profile, on_delete=models.CASCADE)
    feedback = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='student_projects/', blank=True, null=True)
    is_submitted = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.project.title}"