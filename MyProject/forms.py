from django import forms
from .models import Course, Topic, Assessment, Materials, Student_Profile, Student_Progress

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'grade', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
class signupForm(forms.ModelForm):
    class Meta:
        model = Student_Profile
        fields = ['user', 'grade', 'course']
        widgets = {
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'confirm_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            
        }
class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['course', 'topic', 'question', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'answer': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
class QuizeForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['course', 'topic', 'question', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'answer': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }