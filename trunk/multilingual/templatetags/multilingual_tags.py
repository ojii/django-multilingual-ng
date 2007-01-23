from django import template
from django import forms
from django.template import Node, NodeList, Template, Context, resolve_variable
from django.template.loader import get_template, render_to_string
from django.conf import settings
import math
import StringIO
import tokenize

register = template.Library()

from multilingual.models import LANGUAGES

def language_code(language_id):
    """
    Return the code of the language with id=language_id
    """
    return LANGUAGES[language_id - 1][0]
    
register.filter(language_code)

def language_name(language_id):
    """
    Return the name of the language with id=language_id
    """
    return LANGUAGES[language_id - 1][1]
    
register.filter(language_name)
