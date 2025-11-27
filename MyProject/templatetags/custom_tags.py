from django import template
from ..language_utils import get_translation

register = template.Library()

@register.filter
def get(dict_obj, key):
    return dict_obj.get(key, {})


@register.simple_tag
def translate(key, language='en'):
    """Template tag to get translations"""
    return get_translation(key, language)


@register.simple_tag(takes_context=True)
def t(context, key):
    """Shorthand template tag for translations using context language"""
    language = context.get('user_language', 'en')
    return get_translation(key, language)
