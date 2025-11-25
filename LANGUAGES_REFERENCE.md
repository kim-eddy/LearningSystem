# Multi-Language Support - Quick Reference

## 🌍 Supported Languages
- 🇬🇧 English (en)
- 🇰🇪 Kiswahili (sw)
- 🎤 Sheng' (sheng)
- 🇰🇪 Kikuyu (ki)
- 🇸🇴 Kisomali (so)

## 📋 Translations Available

| Key | English | Kiswahili | Sheng' | Kikuyu | Kisomali |
|-----|---------|-----------|--------|--------|----------|
| welcome | Welcome | Karibu | Karibu | Wĩ mwega | Soo dhowow |
| home | Home | Nyumbani | Crib | Mucii | Guriga |
| dashboard | Dashboard | Dashibodi | Dashibodi | Dashibodi | Dashibodi |
| courses | Courses | Kozi | Kozi | Maaraya | Barashada |
| learning_path | Learning Path | Njia ya Kujifunza | Path | Haarĩ ya Kũruta | Jidka Barashada |
| profile | Profile | Wasifu | Profile | Wasifu | Xisaabka |
| settings | Settings | Mipangilio | Settings | Mipango | Sagal |
| logout | Logout | Ondoka | Exit | Thiĩ | Ka bax |
| language | Language | Lugha | Lingo | Rũrĩmeny | Afka |
| assessment | Assessment | Tathmini | Test | Nguo | Tijaabinta |
| my_progress | My Progress | Maendeleo Yangu | My Progress | Maendeleo Makwa | Horumarku |
| leaderboard | Leaderboard | Orodha ya Wasifu | Leaderboard | Orodha ya Mbere | Jadwal Hormumaarka |
| chat | Chat | Mazungumzo | Chat | Menya | Yada |
| help | Help | Msaada | Help | Njira | Caawi |

## 🔧 Implementation Details

### Files Created/Modified

**Created:**
- `MyProject/language_utils.py` - Translation dictionary
- `MyProject/middleware.py` - Language middleware
- `MyProject/templates/language_selector.html` - Language selection page
- `MyProject/templates/language_settings.html` - Preferences page
- `MyProject/migrations/0008_student_profile_preferred_language.py` - Database migration
- `LANGUAGE_IMPLEMENTATION.md` - Full documentation

**Modified:**
- `MyProject/models.py` - Added `preferred_language` field
- `MyProject/forms.py` - Added `LanguagePreferenceForm`
- `MyProject/views.py` - Added language-related views
- `MyProject/urls.py` - Added language routes
- `MyProject/templatetags/custom_tags.py` - Added translation tags
- `LearningSystem/settings.py` - Added middleware

### Database Field

```python
preferred_language = models.CharField(
    max_length=10,
    choices=[
        ('en', 'English'),
        ('sw', 'Kiswahili'),
        ('sheng', "Sheng'"),
        ('ki', 'Kikuyu'),
        ('so', 'Kisomali'),
    ],
    default='en'
)
```

## 🚀 Quick Start

### 1. Run Migrations
```bash
python manage.py migrate MyProject
```

### 2. Use in Templates
```html
{% load custom_tags %}
<h1>{% t 'welcome' %}</h1>
<p>{% t 'language' %}:</p>
```

### 3. Use in Views
```python
from .language_utils import get_translation

language = profile.preferred_language
text = get_translation('welcome', language)
```

### 4. Language Selection Routes
- Initial selection: `/language/`
- Settings page: `/language/settings/`
- API: `/api/translation/welcome/`

## 📝 How User Language is Set

1. **During Signup**: User selects language in signup form
2. **Auto-Middleware**: `LanguageMiddleware` automatically loads user's language
3. **Settings Page**: User can change language at `/language/settings/`
4. **API**: Frontend can fetch translations via `/api/translation/<key>/`

## 🔄 User Flow

```
User Signup
    ↓
Select Language (preferred_language field)
    ↓
Account Created (language saved to database)
    ↓
Middleware loads language on every request
    ↓
Templates use {% t 'key' %} for translations
    ↓
User can change language at /language/settings/
```

## 📱 Frontend Integration Example

```html
<div class="language-menu">
    <a href="{% url 'language_settings' %}">
        {% t 'language' %}
    </a>
</div>
```

## 🔐 Authentication Requirement

- Language selection: Public (no auth required)
- Language settings: Requires login (@login_required)
- Language preference loading: Automatic via middleware

## 💾 Data Storage

Language preference is stored in:
- **Table**: `MyProject_student_profile`
- **Field**: `preferred_language`
- **Type**: VARCHAR(10)
- **Default**: 'en'
- **Null**: False

## 🎯 Next Steps

1. ✅ Apply migrations
2. ✅ Update template base.html with language menu
3. ✅ Add more translations as needed
4. ✅ Test with each language
5. ✅ Customize translation content for each language

## 📞 Support

For adding/updating translations:
1. Edit `MyProject/language_utils.py`
2. Add translations for all 5 languages
3. Use `get_translation()` function to retrieve

For extending to more languages:
1. Add to `LANGUAGE_CHOICES`
2. Create migration
3. Add all translations
4. Update language selector template
