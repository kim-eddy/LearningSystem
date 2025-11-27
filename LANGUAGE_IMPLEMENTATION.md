# Multi-Language Support Implementation Guide

## Overview
Your Learning System now supports multiple local languages:
- **English** (en)
- **Kiswahili** (sw)
- **Sheng'** (sheng)
- **Kikuyu** (ki)
- **Kisomali** (so)

## Features Implemented

### 1. **Language Selection During Signup**
Users select their preferred language when signing up. The `SignupForm` now includes a `preferred_language` field.

### 2. **Language Preferences Page**
Access at `/language/settings/` - allows authenticated users to change their language preference at any time.

### 3. **Automatic Language Context**
A middleware (`LanguageMiddleware`) automatically adds language context to all requests, so your preferred language is always available.

### 4. **Translation System**
- **Location**: `MyProject/language_utils.py`
- Centralized translation dictionary with support for all local languages
- Easy to expand with new translations
- Fallback to English if translation not available

### 5. **Database Migration**
New field `preferred_language` added to `Student_Profile` model with default value of 'en' (English).

## File Structure

```
MyProject/
├── language_utils.py              # Translation dictionary and helper functions
├── middleware.py                  # Language middleware for context injection
├── migrations/
│   └── 0008_student_profile_preferred_language.py  # Database migration
├── forms.py                       # Updated with LanguagePreferenceForm
├── models.py                      # Updated Student_Profile model
├── views.py                       # Added language-related views
├── urls.py                        # Added language URLs
├── templatetags/
│   └── custom_tags.py            # Added translation template tags
└── templates/
    ├── language_selector.html     # Initial language selection
    └── language_settings.html     # User language preferences page
```

## How to Use

### In Python/Views
```python
from .language_utils import get_translation

# Get translation in a specific language
text = get_translation('welcome', 'sw')  # Returns "Karibu"
```

### In Templates
```html
{% load custom_tags %}

<!-- Using the shorthand tag (recommended) -->
<h1>{% t 'welcome' %}</h1>

<!-- Using the full tag -->
<h1>{% translate 'welcome' user_language %}</h1>
```

### In JavaScript/AJAX
```javascript
fetch('/api/translation/welcome/')
  .then(response => response.json())
  .then(data => console.log(data.translation));
```

## Views Created

1. **`select_language()`** - Display language selection page
   - URL: `/language/`
   - Template: `language_selector.html`

2. **`set_language()`** - POST handler to set language (from language selector)
   - URL: `/language/set/`
   - Redirects to home after setting

3. **`language_settings()`** - User language preferences management
   - URL: `/language/settings/`
   - Template: `language_settings.html`
   - Requires authentication

4. **`get_translation_json()`** - API endpoint for translations
   - URL: `/api/translation/<key>/`
   - Returns JSON with translation and current language

## Database Setup

Run migrations to add the language field to the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

Or directly run the migration file:
```bash
python manage.py migrate MyProject 0008_student_profile_preferred_language
```

## Adding New Translations

To add a new translatable term:

1. **Edit `language_utils.py`**:
```python
TRANSLATIONS = {
    'my_new_key': {
        'en': 'English text',
        'sw': 'Swahili text',
        'sheng': "Sheng' text",
        'ki': 'Kikuyu text',
        'so': 'Somali text',
    },
    # ... existing translations
}
```

2. **Use in templates**:
```html
{% t 'my_new_key' %}
```

3. **Use in views**:
```python
text = get_translation('my_new_key', request.user_language)
```

## URL Routes

| URL | View | Purpose |
|-----|------|---------|
| `/language/` | `select_language` | Initial language selection |
| `/language/set/` | `set_language` | Set language (POST) |
| `/language/settings/` | `language_settings` | User preferences page |
| `/api/translation/<key>/` | `get_translation_json` | Translation API |

## Current Translations Available

- welcome
- home
- dashboard
- courses
- learning_path
- profile
- settings
- logout
- language
- select_language
- preferred_language
- save
- cancel
- update
- language_updated
- select_course
- assessment
- my_progress
- leaderboard
- chat
- help
- my_badges
- certificates
- complete_profile
- topics
- resources

## Best Practices

1. **Always use the translation system** for user-facing text
2. **Add translations for all languages** when adding new features
3. **Use the `{% t %}` tag** in templates for cleaner code
4. **Test with different languages** to ensure translations display correctly
5. **Keep translation keys descriptive** (e.g., `page_title_courses` not `pt`)

## Extending the System

### Add a New Language
1. Add language choice to `LANGUAGE_CHOICES` in `language_utils.py`
2. Add language options to `Student_Profile.LANGUAGE_CHOICES` in `models.py`
3. Create a new migration for the model update
4. Add translations for all existing keys
5. Update migration `0008_...` if needed

### Connect to Navigation
Update your base template to include language menu:
```html
<a href="{% url 'language_settings' %}">
    {% t 'language' %}
</a>
```

## Notes
- Default language is English (en)
- Language preference is stored per user in the database
- The middleware ensures every request has language context
- Translations fall back to English if a language is missing a translation

## Support
For issues or adding more translations, refer to `language_utils.py` for the full translation dictionary.
