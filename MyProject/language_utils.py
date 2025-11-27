# Language translations and utilities for the Learning System
# Supports: English, Kiswahili, Sheng', Kikuyu, Kisomali

LANGUAGE_CHOICES = {
    'en': 'English',
    'sw': 'Kiswahili',
    'sheng': "Sheng'",
    'ki': 'Kikuyu',
    'so': 'Kisomali',
}

# Translation dictionary
TRANSLATIONS = {
    # General UI elements
    'welcome': {
        'en': 'Welcome',
        'sw': 'Karibu',
        'sheng': 'Karibu',
        'ki': 'Wĩ mwega',
        'so': 'Soo dhowow',
    },
    'home': {
        'en': 'Home',
        'sw': 'Nyumbani',
        'sheng': 'Crib',
        'ki': 'Mucii',
        'so': 'Guriga',
    },
    'dashboard': {
        'en': 'Dashboard',
        'sw': 'Dashibodi',
        'sheng': 'Dashibodi',
        'ki': 'Dashibodi',
        'so': 'Dashibodi',
    },
    'courses': {
        'en': 'Courses',
        'sw': 'Kozi',
        'sheng': 'Kozi',
        'ki': 'Maaraya',
        'so': 'Barashada',
    },
    'learning_path': {
        'en': 'Learning Path',
        'sw': 'Njia ya Kujifunza',
        'sheng': 'Path',
        'ki': 'Haarĩ ya Kũruta',
        'so': 'Jidka Barashada',
    },
    'profile': {
        'en': 'Profile',
        'sw': 'Wasifu',
        'sheng': 'Profile',
        'ki': 'Wasifu',
        'so': 'Xisaabka',
    },
    'settings': {
        'en': 'Settings',
        'sw': 'Mipangilio',
        'sheng': 'Settings',
        'ki': 'Mipango',
        'so': 'Sagal',
    },
    'logout': {
        'en': 'Logout',
        'sw': 'Ondoka',
        'sheng': 'Exit',
        'ki': 'Thiĩ',
        'so': 'Ka bax',
    },
    'language': {
        'en': 'Language',
        'sw': 'Lugha',
        'sheng': 'Lingo',
        'ki': 'Rũrĩmeny',
        'so': 'Afka',
    },
    'select_language': {
        'en': 'Select Your Language',
        'sw': 'Chagua Lugha Yako',
        'sheng': 'Pick Your Lingo',
        'ki': 'Hota Rũrĩmeny Rĩako',
        'so': 'Dooro Afkaaga',
    },
    'preferred_language': {
        'en': 'Preferred Language',
        'sw': 'Lugha Inayopendekezwa',
        'sheng': 'Your Preferred Lingo',
        'ki': 'Rũrĩmeny Rũrĩa Ũrathii',
        'so': 'Afka Aad Jeclida',
    },
    'save': {
        'en': 'Save',
        'sw': 'Hifadhi',
        'sheng': 'Save',
        'ki': 'Ruta',
        'so': 'Kaydi',
    },
    'cancel': {
        'en': 'Cancel',
        'sw': 'Kataa',
        'sheng': 'Cancel',
        'ki': 'Menya',
        'so': 'Jooji',
    },
    'update': {
        'en': 'Update',
        'sw': 'Sasisha',
        'sheng': 'Update',
        'ki': 'Sasisha',
        'so': 'Cusbuur',
    },
    'language_updated': {
        'en': 'Language updated successfully!',
        'sw': 'Lugha imesasishwa kwa mafanikio!',
        'sheng': 'Lingo updated successfully!',
        'ki': 'Rũrĩmeny ryasasishwe ĩrĩa yothe!',
        'so': 'Afka waa kusuubnoowday!',
    },
    'select_course': {
        'en': 'Select Course',
        'sw': 'Chagua Kozi',
        'sheng': 'Pick Course',
        'ki': 'Hota Maaraya',
        'so': 'Dooro Barashada',
    },
    'assessment': {
        'en': 'Assessment',
        'sw': 'Tathmini',
        'sheng': 'Test',
        'ki': 'Nguo',
        'so': 'Tijaabinta',
    },
    'my_progress': {
        'en': 'My Progress',
        'sw': 'Maendeleo Yangu',
        'sheng': 'My Progress',
        'ki': 'Maendeleo Makwa',
        'so': 'Horumarku',
    },
    'leaderboard': {
        'en': 'Leaderboard',
        'sw': 'Orodha ya Wasifu',
        'sheng': 'Leaderboard',
        'ki': 'Orodha ya Mbere',
        'so': 'Jadwal Hormumaarka',
    },
    'chat': {
        'en': 'Chat',
        'sw': 'Mazungumzo',
        'sheng': 'Chat',
        'ki': 'Menya',
        'so': 'Yada',
    },
    'help': {
        'en': 'Help',
        'sw': 'Msaada',
        'sheng': 'Help',
        'ki': 'Njira',
        'so': 'Caawi',
    },
    'my_badges': {
        'en': 'My Badges',
        'sw': 'Mabiji Yangu',
        'sheng': 'My Badges',
        'ki': 'Mabiji Makwa',
        'so': 'Magulguliyo Igu Jirta',
    },
    'certificates': {
        'en': 'Certificates',
        'sw': 'Vyeti',
        'sheng': 'Certs',
        'ki': 'Vyeti',
        'so': 'Shahaadooyin',
    },
    'complete_profile': {
        'en': 'Complete Your Profile',
        'sw': 'Kamata Wasifu Wako',
        'sheng': 'Complete Profile',
        'ki': 'Camba Wasifu Wako',
        'so': 'Kammala Xisaabka',
    },
    'topics': {
        'en': 'Topics',
        'sw': 'Mada',
        'sheng': 'Topics',
        'ki': 'Maaraya',
        'so': 'Mada',
    },
    'resources': {
        'en': 'Resources',
        'sw': 'Rasilimali',
        'sheng': 'Resources',
        'ki': 'Maitho',
        'so': 'Dekada',
    },
}


def get_translation(key, language='en'):
    """
    Get translated text for a given key in the specified language.
    Falls back to English if translation not available.
    
    Args:
        key (str): Translation key
        language (str): Language code (en, sw, sheng, ki, so)
    
    Returns:
        str: Translated text or original key if not found
    """
    if key in TRANSLATIONS:
        translation = TRANSLATIONS[key].get(language, TRANSLATIONS[key].get('en', key))
        return translation
    return key


def get_language_name(language_code):
    """Get the full name of a language from its code."""
    return LANGUAGE_CHOICES.get(language_code, 'English')


def get_available_languages():
    """Get all available languages as a list of tuples."""
    return [(code, name) for code, name in LANGUAGE_CHOICES.items()]
