# Middleware to automatically add language context to all requests

from .models import Student_Profile
from .language_utils import get_translation



class LanguageMiddleware:
    """
    Middleware to automatically add language preferences to request context.
    This allows all views and templates to access the user's preferred language.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set default language
        request.user_language = 'en'
        request.get_translation = lambda key, lang=None: get_translation(
            key, 
            lang or getattr(request, 'user_language', 'en')
        )
        
        # Get user's preferred language if authenticated
        if request.user.is_authenticated:
            try:
                profile = Student_Profile.objects.get(user=request.user)
                request.user_language = profile.preferred_language
            except Student_Profile.DoesNotExist:
                pass
        
        response = self.get_response(request)
        return response
