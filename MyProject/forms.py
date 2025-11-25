from django import forms
from django.contrib.auth.models import User
from .models import Course, Topic, Assessment, Materials, Student_Profile, Student_Progress, Grade, School
from .language_utils import get_available_languages


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'grade', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40, 'class': 'form-control'}),
        }


class SignupForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Student_Profile
        fields = ['username', 'first_name', 'last_name', 'email', 
                 'password', 'confirm_password', 'phone_number', 
                 'school', 'grade', 'preferred_language']
        
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'preferred_language': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['school'].queryset = School.objects.filter(subscription_active=True)
        self.fields['grade'].queryset = Grade.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        if User.objects.filter(username=cleaned_data.get('username')).exists():
            raise forms.ValidationError("Username already exists.")
            
        if User.objects.filter(email=cleaned_data.get('email')).exists():
            raise forms.ValidationError("Email already registered.")

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )

        student_profile = Student_Profile(
            user=user,
            phone_number=self.cleaned_data['phone_number'],
            school=self.cleaned_data['school'],  
            grade=self.cleaned_data['grade'],
            preferred_language=self.cleaned_data.get('preferred_language', 'en'),
        )

        if commit:
            student_profile.save()

        return student_profile


# Combined assessment form that can be used for both purposes with a type field
class AssessmentForm(forms.ModelForm):
    ASSESSMENT_TYPES = [
        ('quiz', 'Quiz'),
        ('test', 'Test'),
        ('exam', 'Exam'),
    ]
    
    type = forms.ChoiceField(choices=ASSESSMENT_TYPES)

    class Meta:
        model = Assessment
        fields = ['course', 'topic', 'question', 'answer']  
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class StudentProfileUpdateForm(forms.ModelForm):
    INTEREST_CHOICES = [
        ('Data Science', 'Data Science'),
        ('Web Development', 'Web Development'),
        ('Machine Learning', 'Machine Learning'),
        ('Python', 'Python'),
        ('Cybersecurity', 'Cybersecurity'),
        ('AI', 'AI'),
    ]

    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = Student_Profile
        fields = ['phone_number', 'email', 'interests']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure current selected interests show up
        if self.instance and isinstance(self.instance.interests, list):
            self.initial['interests'] = self.instance.interests

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.interests = self.cleaned_data.get('interests', [])
        if commit:
            profile.save()
        return profile


class LanguagePreferenceForm(forms.ModelForm):
    """Form for users to select their preferred language"""
    
    class Meta:
        model = Student_Profile
        fields = ['preferred_language']
        widgets = {
            'preferred_language': forms.RadioSelect(attrs={
                'class': 'form-check-input language-radio'
            }),
        }
        labels = {
            'preferred_language': 'Select Your Preferred Language'
        }