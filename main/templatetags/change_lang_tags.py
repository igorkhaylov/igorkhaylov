# from django import template
from django.template import Library

register = Library()


@register.simple_tag()
def get_lang(request):
    if "/ru/" in request.path:
        lang_url = request.path.replace("ru", "en")
        lang = "EN"
    else:
        lang_url = request.path.replace("en", "ru")
        lang = "RU"
    return {"lang_url": lang_url,
            "lang": lang,
            }
