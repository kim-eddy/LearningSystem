# Multi-Language Support - Code Examples

## 📝 Using Translations in Templates

### Basic Usage with {% t %} Tag

```html
{% load custom_tags %}

<h1>{% t 'welcome' %}</h1>
<p>{% t 'language' %}</p>
<a href="#">{% t 'home' %}</a>
```

### With Full Tag

```html
{% load custom_tags %}

<h1>{% translate 'welcome' user_language %}</h1>
```

### Complete Example Page

```html
{% load custom_tags %}
<!DOCTYPE html>
<html>
<head>
    <title>{% t 'dashboard' %}</title>
</head>
<body>
    <nav>
        <a href="/">{% t 'home' %}</a>
        <a href="/courses/">{% t 'courses' %}</a>
        <a href="/student/profile/">{% t 'profile' %}</a>
        <a href="/language/settings/">{% t 'language' %}</a>
    </nav>
    
    <h1>{% t 'welcome' %}, {{ user.first_name }}!</h1>
    
    <section>
        <h2>{% t 'my_progress' %}</h2>
        <!-- Progress content -->
    </section>
    
    <footer>
        <p>© 2025 Learning System - {% t 'language' %}: {{ user_language }}</p>
    </footer>
</body>
</html>
```

## 🐍 Using Translations in Views

### Basic Translation in Views

```python
from .language_utils import get_translation
from .models import Student_Profile

@login_required
def course_detail(request, course_id):
    profile = Student_Profile.objects.get(user=request.user)
    language = profile.preferred_language
    
    # Get translations
    page_title = get_translation('courses', language)
    
    context = {
        'title': page_title,
        'user_language': language
    }
    return render(request, 'course_detail.html', context)
```

### Using Middleware Context

```python
@login_required
def student_profile(request):
    # Language automatically available via middleware
    language = request.user_language
    
    # Get translation
    welcome_msg = get_translation('welcome', language)
    
    context = {
        'message': welcome_msg,
    }
    return render(request, 'profile.html', context)
```

### Using Request Method

```python
@login_required
def dashboard(request):
    # Using the request.get_translation method
    welcome = request.get_translation('welcome')
    dashboard_title = request.get_translation('dashboard')
    
    context = {
        'welcome': welcome,
        'title': dashboard_title,
    }
    return render(request, 'dashboard.html', context)
```

### Setting Language Preference

```python
from django.contrib import messages
from .language_utils import get_translation

@login_required
def language_settings(request):
    profile = Student_Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        language = request.POST.get('language')
        profile.preferred_language = language
        profile.save()
        
        # Show success message in chosen language
        success_msg = get_translation('language_updated', language)
        messages.success(request, success_msg)
        
        return redirect('language_settings')
    
    return render(request, 'language_settings.html', {'profile': profile})
```

## 🔌 Using Translations in JavaScript/AJAX

### Fetch Translation via API

```javascript
// Get a single translation
async function getTranslation(key) {
    const response = await fetch(`/api/translation/${key}/`);
    const data = await response.json();
    console.log(data.translation);  // The translated text
    console.log(data.language);      // Current user language
}

getTranslation('welcome');
```

### Dynamic UI Updates

```javascript
// Update UI when user changes language
async function updateLanguage(languageCode) {
    // Make request to set language
    const formData = new FormData();
    formData.append('language', languageCode);
    
    const response = await fetch('/language/set/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    });
    
    if (response.ok) {
        location.reload();  // Reload to apply language changes
    }
}

// Usage
document.getElementById('lang-selector').addEventListener('change', (e) => {
    updateLanguage(e.target.value);
});
```

### Multiple Translation Fetches

```javascript
// Get multiple translations at once
async function getTranslations(keys) {
    const translations = {};
    
    for (const key of keys) {
        const response = await fetch(`/api/translation/${key}/`);
        const data = await response.json();
        translations[key] = data.translation;
    }
    
    return translations;
}

// Usage
getTranslations(['welcome', 'courses', 'profile', 'settings']).then(trans => {
    console.log(trans);  // All translations loaded
});
```

## 📋 Form Examples

### Signup Form with Language Selection

```html
{% load static %}
<form method="post" action="{% url 'signup' %}">
    {% csrf_token %}
    
    <div class="form-group">
        <label for="username">{% t 'username' %}</label>
        {{ form.username }}
    </div>
    
    <div class="form-group">
        <label for="email">{% t 'email' %}</label>
        {{ form.email }}
    </div>
    
    <!-- Language Selection -->
    <div class="form-group">
        <label for="language">{% t 'select_language' %}</label>
        {{ form.preferred_language }}
    </div>
    
    <button type="submit">{% t 'save' %}</button>
</form>
```

### Language Preferences Form

```html
{% load custom_tags %}
<form method="post" action="{% url 'language_settings' %}">
    {% csrf_token %}
    
    <h2>{% t 'language' %}</h2>
    
    <div class="form-check">
        <input type="radio" id="lang_en" name="preferred_language" 
               value="en" {% if profile.preferred_language == 'en' %}checked{% endif %}>
        <label for="lang_en">🇬🇧 English</label>
    </div>
    
    <div class="form-check">
        <input type="radio" id="lang_sw" name="preferred_language" 
               value="sw" {% if profile.preferred_language == 'sw' %}checked{% endif %}>
        <label for="lang_sw">🇰🇪 Kiswahili</label>
    </div>
    
    <div class="form-check">
        <input type="radio" id="lang_sheng" name="preferred_language" 
               value="sheng" {% if profile.preferred_language == 'sheng' %}checked{% endif %}>
        <label for="lang_sheng">🎤 Sheng'</label>
    </div>
    
    <div class="form-check">
        <input type="radio" id="lang_ki" name="preferred_language" 
               value="ki" {% if profile.preferred_language == 'ki' %}checked{% endif %}>
        <label for="lang_ki">🇰🇪 Kikuyu</label>
    </div>
    
    <div class="form-check">
        <input type="radio" id="lang_so" name="preferred_language" 
               value="so" {% if profile.preferred_language == 'so' %}checked{% endif %}>
        <label for="lang_so">🇸🇴 Kisomali</label>
    </div>
    
    <button type="submit">{% t 'save' %}</button>
</form>
```

## 🎯 Complete Page Example

### Dashboard with All Languages Features

```html
{% load custom_tags %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% t 'dashboard' %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">{% t 'dashboard' %}</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/courses/">{% t 'courses' %}</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/student/progress/">{% t 'my_progress' %}</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/leaderboard/">{% t 'leaderboard' %}</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/student/profile/">{% t 'profile' %}</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/language/settings/">🌍 {% t 'language' %}</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/logout/">{% t 'logout' %}</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <div class="container mt-5">
        <h1>{% t 'welcome' %}, {{ user.first_name }}!</h1>
        
        <div class="row mt-4">
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{% t 'courses' %}</h5>
                        <p class="card-text">{{ enrolled_courses_count }}</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{% t 'my_badges' %}</h5>
                        <p class="card-text">{{ badges_count }}</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{% t 'my_progress' %}</h5>
                        <p class="card-text">{{ progress_percentage }}%</p>
                    </div>
                </div>
            </div>
            
            <div class="col-md-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{% t 'language' %}</h5>
                        <p class="card-text">{{ current_language }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

## 🔧 Python Utility Examples

### Adding Helper Functions

```python
# In language_utils.py or views.py
from .language_utils import get_translation, LANGUAGE_CHOICES

def get_user_language(user):
    """Helper to get user's preferred language"""
    try:
        profile = Student_Profile.objects.get(user=user)
        return profile.preferred_language
    except Student_Profile.DoesNotExist:
        return 'en'

def translate_page(request, keys):
    """Helper to translate multiple keys at once"""
    language = getattr(request, 'user_language', 'en')
    translations = {}
    for key in keys:
        translations[key] = get_translation(key, language)
    return translations

# Usage in views
@login_required
def course_list(request):
    # Translate multiple terms
    translations = translate_page(request, ['courses', 'select_course', 'topics'])
    
    context = {
        'translations': translations,
        'courses': Course.objects.all(),
    }
    return render(request, 'course_list.html', context)
```

## 📝 Tips & Best Practices

1. **Always use translation keys** - Never hardcode text in templates
2. **Keep keys descriptive** - `page_title_courses` is better than `pt`
3. **Add fallback** - Always have English translation as fallback
4. **Test all languages** - Verify layout doesn't break with longer translations
5. **Cache translations** - Consider caching if many translation calls
6. **Use consistent naming** - `verb_noun` pattern for keys
7. **Document new keys** - Add comments explaining the context

---

**Note**: All examples use the `{% t %}` shorthand template tag for cleaner code. This tag automatically uses the current user's language from middleware context.
