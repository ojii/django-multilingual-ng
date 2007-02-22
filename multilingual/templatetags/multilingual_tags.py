from django import template
from django import forms
from django.template import Node, NodeList, Template, Context, resolve_variable
from django.template.loader import get_template, render_to_string
from django.conf import settings
import math
import StringIO
import tokenize

register = template.Library()

from multilingual.languages import get_language_code, get_language_name

def language_code(language_id):
    """
    Return the code of the language with id=language_id
    """
    return get_language_code(language_id)
    
register.filter(language_code)

def language_name(language_id):
    """
    Return the name of the language with id=language_id
    """
    return get_language_name(language_id)
    
register.filter(language_name)

class EditTranslationNode(template.Node):
    def __init__(self, form_name, field_name, language=None):
        self.form_name = form_name
        self.field_name = field_name
        self.language = language

    def render(self, context):
        return "-todo-"

def do_edit_translation(parser, token):
    bits = token.split_contents()
    if len(bits) not in [3, 4]:
        raise template.TemplateSyntaxError, \
              "%r tag requires 3 or 4 arguments" % bits[0]
    return EditTranslationNode(*bits[1:])
        
        
register.tag('edit_translation', do_edit_translation)
