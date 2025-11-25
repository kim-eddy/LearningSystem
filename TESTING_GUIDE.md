# Multi-Language Support - Testing Guide

## 🧪 Testing Checklist

### Pre-Setup
- [ ] Backup database
- [ ] Check Django version (requires 3.2+)
- [ ] Verify all files are in place

### Setup Tests
- [ ] Run: `python manage.py migrate`
- [ ] Check migration succeeded
- [ ] Database field `preferred_language` added to `student_profile`

### Signup Flow Tests

**Test 1: Signup with Language Selection**
1. Navigate to `/signup/`
2. Fill all required fields
3. Verify language options appear (English, Kiswahili, Sheng', Kikuyu, Kisomali)
4. Select "Kiswahili"
5. Submit form
6. Verify user created with `preferred_language = 'sw'`

**Test 2: Default Language on Signup**
1. Create user without selecting language
2. Verify defaults to 'en' in database

**Test 3: All Languages in Dropdown**
- [ ] English (en)
- [ ] Kiswahili (sw)
- [ ] Sheng' (sheng)
- [ ] Kikuyu (ki)
- [ ] Kisomali (so)

### Login & Middleware Tests

**Test 4: Middleware Loads User Language**
1. Login as user with `preferred_language = 'sw'`
2. Check browser console or template context
3. Verify `user_language = 'sw'` is set
4. Navigate to different pages
5. Verify language persists

**Test 5: Anonymous User Gets Default Language**
1. Logout
2. Navigate to site
3. Verify `user_language = 'en'` (default)

### Language Selection Page Tests

**Test 6: Initial Language Selection**
1. Navigate to `/language/`
2. Verify all 5 languages display with flags
3. Select a language
4. Click "Continue"
5. Should redirect to `/home/`
6. Check database - language should be saved

**Test 7: Language Selector UI**
- [ ] Radio buttons visible and functional
- [ ] Flag emojis display correctly
- [ ] "Continue" button works
- [ ] "Skip for Now" button works
- [ ] Mobile responsive (test on phone size)

### Language Settings Page Tests

**Test 8: Access Language Settings**
1. Login as authenticated user
2. Navigate to `/language/settings/`
3. Verify language preferences form displays
4. All 5 languages should be radio options
5. Current language should be selected

**Test 9: Change Language Preference**
1. Select different language (e.g., Kikuyu)
2. Click "Save Preference"
3. Should see success message: "Language updated successfully!"
4. Navigate to different page
5. Verify all text uses new language

**Test 10: Anonymous Access Protection**
1. Logout
2. Try to access `/language/settings/`
3. Should redirect to login page

### Template Translation Tests

**Test 11: Template Tags Work**
```html
{% load custom_tags %}
<h1>{% t 'welcome' %}</h1>
```
- [ ] Text displays in correct language
- [ ] No errors in console
- [ ] Works with user_language context

**Test 12: Different Languages in Templates**
For each language, verify these translations:
1. **English (en)**
   - "Welcome" displays as "Welcome"
   - "Home" displays as "Home"
   - "Courses" displays as "Courses"

2. **Kiswahili (sw)**
   - "Welcome" displays as "Karibu"
   - "Home" displays as "Nyumbani"
   - "Courses" displays as "Kozi"

3. **Sheng' (sheng)**
   - "Welcome" displays as "Karibu"
   - "Home" displays as "Crib"
   - "Courses" displays as "Kozi"

4. **Kikuyu (ki)**
   - "Welcome" displays as "Wĩ mwega"
   - "Home" displays as "Mucii"
   - "Courses" displays as "Maaraya"

5. **Kisomali (so)**
   - "Welcome" displays as "Soo dhowow"
   - "Home" displays as "Guriga"
   - "Courses" displays as "Barashada"

### API Tests

**Test 13: Translation API Endpoint**
```bash
# Get translation for 'welcome'
curl http://localhost:8000/api/translation/welcome/

# Expected response:
{
  "translation": "Welcome",
  "language": "en"
}
```

**Test 14: API with Different Languages**
1. Authenticate as user with language='sw'
2. Call `/api/translation/welcome/`
3. Should return "Karibu" as translation

### Database Tests

**Test 15: Database Persistence**
1. Change user language to Kikuyu
2. Restart Django server
3. Login again
4. Verify language is still Kikuyu
5. Check database directly: `SELECT preferred_language FROM student_profile WHERE user_id=X`

**Test 16: Migration Integrity**
```bash
# Check migration status
python manage.py showmigrations MyProject

# Output should show migration 0008 as applied [X]
```

### Edge Cases

**Test 17: Invalid Language Code**
1. Manually set invalid language in database (e.g., 'xx')
2. Login
3. Should fallback to 'en' gracefully

**Test 18: Multiple Language Switches**
1. Login
2. Change language to Kiswahili → Save
3. Change language to Kikuyu → Save
4. Change language to English → Save
5. Verify each change persists

**Test 19: Concurrent User Languages**
1. Create 2 user accounts with different languages
2. Login to user 1 (English)
3. In another browser, login to user 2 (Kiswahili)
4. Verify each sees their language
5. Switch tabs back and forth
6. Verify no mixing of languages

### Performance Tests

**Test 20: Middleware Performance**
1. Enable Django debug toolbar or profiling
2. Check middleware adds < 5ms to request time
3. Verify no N+1 queries

**Test 21: Translation Lookups**
1. Use django-silk or similar
2. Verify `get_translation()` calls don't query database
3. Should use only in-memory dictionary

### Browser Compatibility

**Test 22: Cross-Browser Testing**
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

**Test 23: Responsive Design**
- [ ] Desktop (1920px width)
- [ ] Tablet (768px width)
- [ ] Mobile (375px width)

### Integration Tests

**Test 24: Full User Journey**
1. Signup with language=Kiswahili
2. Login
3. All UI shows Kiswahili
4. Change to Kikuyu in settings
5. All UI shows Kikuyu
6. Logout
7. Login as different user with English
8. See English UI

**Test 25: Navigation Links**
1. Login with Kiswahili language
2. Click all navigation links
3. Verify all pages maintain Kiswahili language
4. Check no console errors

## 🐛 Debugging Steps

### If Middleware Not Working
```python
# Add to view for testing
print(f"User language: {request.user_language}")
print(f"Has get_translation: {hasattr(request, 'get_translation')}")
```

### If Translations Not Showing
```python
# Check if key exists
from .language_utils import TRANSLATIONS
print('welcome' in TRANSLATIONS)  # Should be True

# Check language
from .models import Student_Profile
profile = Student_Profile.objects.get(user=user)
print(f"Language: {profile.preferred_language}")
```

### If Template Tags Not Working
```python
# Check if loaded
{% load custom_tags %}
<!-- This should work -->
{% t 'welcome' %}
```

### If Database Migration Failed
```bash
# Check migration status
python manage.py showmigrations MyProject

# If migration shows as unapplied, try:
python manage.py migrate MyProject 0008_student_profile_preferred_language

# If stuck, reset and retry:
python manage.py migrate MyProject zero  # WARNING: Resets all
python manage.py migrate MyProject
```

## 📊 Test Results Template

```
TEST ENVIRONMENT
- Django Version: ___
- Python Version: ___
- Database: ___
- Browser: ___

RESULTS
Setup: [PASS / FAIL]
Signup: [PASS / FAIL]
Middleware: [PASS / FAIL]
Language Selection: [PASS / FAIL]
Settings Page: [PASS / FAIL]
Templates: [PASS / FAIL]
API: [PASS / FAIL]
Database: [PASS / FAIL]
Performance: [PASS / FAIL]
Browser Compat: [PASS / FAIL]

NOTES:
- Issue 1: ___
- Issue 2: ___

BLOCKERS:
- [ ] None
- [ ] Blocking issue (describe)
```

## 🚀 Quick Test Commands

```bash
# Run specific tests
python manage.py test MyProject.tests.LanguageTests

# Check template rendering
python manage.py shell
>>> from MyProject.language_utils import get_translation
>>> get_translation('welcome', 'sw')
'Karibu'

# Test middleware
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/api/translation/welcome/
```

## ✅ Sign-off Checklist

- [ ] All migrations applied successfully
- [ ] No database errors
- [ ] Signup includes language selection
- [ ] Language settings page accessible
- [ ] Templates render correct translations
- [ ] Language persists across pages
- [ ] Middleware works for authenticated users
- [ ] API endpoints respond correctly
- [ ] No console errors
- [ ] Mobile responsive
- [ ] Cross-browser compatible
- [ ] Performance acceptable
- [ ] All 5 languages tested
- [ ] Edge cases handled
- [ ] Documentation complete

---

**Testing Completed**: ___________  
**Tester**: ___________  
**Status**: [ ] Ready for Production [ ] Needs Fixes
