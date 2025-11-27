# 🚀 Quick Start Guide - Multi-Language Support

## 📦 What's New

Your Learning System now supports 5 local languages! Users can select and switch between:
- 🇬🇧 English
- 🇰🇪 Kiswahili  
- 🎤 Sheng'
- 🇰🇪 Kikuyu
- 🇸🇴 Kisomali

## ⚡ 30-Second Setup

1. **Run Migration**
   ```bash
   python manage.py migrate
   ```

2. **Test Language Selection**
   ```
   Visit: http://localhost:8000/language/
   ```

3. **Test Language Settings**
   ```
   Visit: http://localhost:8000/language/settings/
   ```

Done! 🎉

## 📂 What Was Added

| Item | Location | Purpose |
|------|----------|---------|
| Language Model Field | `models.py` | Store user language preference |
| Translation Dictionary | `language_utils.py` | All translations for 5 languages |
| Middleware | `middleware.py` | Auto-load language for every request |
| Language Views | `views.py` | Handle language selection/changes |
| Language Routes | `urls.py` | `/language/`, `/language/settings/` |
| Template Tags | `custom_tags.py` | `{% t 'key' %}` for translations |
| Database Migration | `migrations/` | Add language field to DB |
| UI Templates | `templates/` | Language selector & settings pages |

## 🎯 How Users Select Language

### Option 1: During Signup
When users sign up, they select their preferred language in the signup form.

### Option 2: After Login
Users can change language anytime at `/language/settings/`

### Option 3: First Visit
Navigate to `/language/` to see language selector

## 💻 How Developers Use It

### In Templates (Easy ✨)
```html
{% load custom_tags %}
<h1>{% t 'welcome' %}</h1>
```

### In Views
```python
from .language_utils import get_translation
text = get_translation('welcome', user_language)
```

### In JavaScript
```javascript
fetch('/api/translation/welcome/')
  .then(r => r.json())
  .then(data => console.log(data.translation));
```

## 📋 Common Tasks

### Display Translated Text in Template
```html
{% load custom_tags %}
<p>{% t 'my_progress' %}</p>
```

### Change Language Dynamically
1. User visits `/language/settings/`
2. Selects new language
3. Clicks "Save Preference"
4. All UI updates to new language

### Add New Translation
1. Edit `MyProject/language_utils.py`
2. Add new entry to `TRANSLATIONS`:
```python
'my_new_key': {
    'en': 'English text',
    'sw': 'Swahili text',
    'sheng': "Sheng' text",
    'ki': 'Kikuyu text',
    'so': 'Somali text',
}
```
3. Use: `{% t 'my_new_key' %}`

## 🔗 Important URLs

| URL | Purpose |
|-----|---------|
| `/language/` | Select language (public) |
| `/language/set/` | Save language (POST) |
| `/language/settings/` | Change language (authenticated users) |
| `/api/translation/<key>/` | Get translation via API |

## 🔐 Authentication

- Language selector: **Public** (anyone can access)
- Language settings: **Login Required** (only authenticated users)
- Language middleware: **Automatic** (works everywhere)

## 📊 Database Schema

```sql
ALTER TABLE MyProject_student_profile 
ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en';

-- Values: 'en', 'sw', 'sheng', 'ki', 'so'
```

## 🎨 UI Features

**Language Selector Page** (`/language/`)
- 5 language options with flags
- Radio button selection
- "Continue" to proceed
- "Skip for Now" option
- Mobile responsive
- Beautiful gradient design

**Language Settings Page** (`/language/settings/`)
- Current language highlighted
- Easy switching
- Success confirmation
- Requires authentication
- Bootstrap-based styling

## 🧪 Quick Test

```bash
# 1. Run migrations
python manage.py migrate

# 2. Start server
python manage.py runserver

# 3. Test language selector
# Visit: http://localhost:8000/language/

# 4. Test settings page (after login)
# Visit: http://localhost:8000/language/settings/

# 5. Test API
# Visit: http://localhost:8000/api/translation/welcome/
```

## 📝 Key Features

✅ **5 Local Languages**
- English, Kiswahili, Sheng', Kikuyu, Kisomali

✅ **User Preference Storage**
- Saved to database per user
- Persists across sessions

✅ **Automatic Language Loading**
- Middleware auto-detects user language
- Available on every page

✅ **Easy Template Integration**
- Simple `{% t 'key' %}` syntax
- No configuration needed

✅ **Responsive Design**
- Works on desktop, tablet, mobile

✅ **Fallback to English**
- If translation missing, shows English

✅ **Translation API**
- Frontend can fetch translations
- Returns JSON

## 🚨 Troubleshooting

### Translations Not Showing
1. Verify middleware is enabled in `settings.py`
2. Check migration ran: `python manage.py showmigrations`
3. Reload page and clear browser cache

### Language Not Persisting
1. Check database field exists: `python manage.py dbshell`
2. Verify user record: `SELECT * FROM MyProject_student_profile WHERE user_id=X`

### Template Tags Not Working
1. Add `{% load custom_tags %}` at top of template
2. Check syntax: `{% t 'key' %}` (not `{{ t 'key' }}`)

## 📚 Documentation Files

| File | Contains |
|------|----------|
| `IMPLEMENTATION_SUMMARY.md` | Complete overview |
| `LANGUAGE_IMPLEMENTATION.md` | Detailed implementation guide |
| `LANGUAGES_REFERENCE.md` | Translation reference table |
| `CODE_EXAMPLES.md` | Code samples for all features |
| `TESTING_GUIDE.md` | Comprehensive testing checklist |
| `SETUP_LANGUAGES.sh` | Setup script |

## 🎓 Learning Path

**New to this feature?** Read in order:
1. This file (Quick Start)
2. `LANGUAGES_REFERENCE.md` (See available translations)
3. `CODE_EXAMPLES.md` (Learn usage patterns)
4. `IMPLEMENTATION_SUMMARY.md` (Understand architecture)

**Need to extend?** Read:
1. `LANGUAGE_IMPLEMENTATION.md` (How to add languages)
2. `CODE_EXAMPLES.md` (Implementation patterns)

**Testing?** Read:
1. `TESTING_GUIDE.md` (Complete testing checklist)

## 🔄 User Flow

```
User Signs Up
    ↓
Selects Language
    ↓
Account Created with Language Saved
    ↓
User Logs In
    ↓
Middleware Auto-loads Language
    ↓
All UI Shows Selected Language
    ↓
User Can Change at /language/settings/
    ↓
Language Updates Across Site
```

## ⚙️ Technical Stack

- **Backend**: Django 5.2+
- **Database**: MySQL/PostgreSQL (any Django-supported DB)
- **Frontend**: Bootstrap 5.3
- **Storage**: User's `Student_Profile.preferred_language`
- **Architecture**: Middleware + Template Tags + Translation Dictionary

## 🎁 Bonus Features

- 🔄 Easy language switching
- 💾 Persistent user preference
- 🌐 API for frontend translations
- 📱 Mobile responsive UI
- 🎨 Beautiful language selector
- 📊 30+ translated terms
- ♿ Fallback support
- 🚀 Zero-config setup

## 📞 Need Help?

1. Check `CODE_EXAMPLES.md` for usage patterns
2. Review `LANGUAGE_IMPLEMENTATION.md` for architecture
3. Run `TESTING_GUIDE.md` to verify setup
4. Check Django logs: `python manage.py shell`

## 🎯 Next Steps

1. ✅ Run migration: `python manage.py migrate`
2. ✅ Test language selection: `/language/`
3. ✅ Test settings page: `/language/settings/` (after login)
4. ✅ Update templates with `{% t %}` tags
5. ✅ Add more translations as needed

## 🏁 Summary

You now have a complete, production-ready multi-language support system for your Learning System! Users can:
- Select language during signup
- Change language anytime
- See entire UI in their chosen language
- Have preference saved across sessions

Everything is documented, tested, and ready to use. Start with the quick test commands above!

---

**Questions?** Refer to the comprehensive documentation files included in the project.

**Happy language switching! 🌍**
