from django import template
from django import forms
from django.template import Node, NodeList, Template, Context, resolve_variable
from django.template.loader import get_template, render_to_string
from django.conf import settings
from django.utils.html import escape
from multilingual.languages import get_language_idx, get_default_language
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
        form = resolve_variable(self.form_name, context)
        model = form.manipulator.model
        trans_model = model._meta.translation_model
        if self.language:
            language_id = self.language.resolve(context)
        else:
            language_id = get_default_language()
        real_name = "%s.%s.%s.%s" % (self.form_name,
                                     trans_model._meta.object_name.lower(),
                                     get_language_idx(language_id),
                                     self.field_name)
        return str(resolve_variable(real_name, context))

def do_edit_translation(parser, token):
    bits = token.split_contents()
    if len(bits) not in [3, 4]:
        raise template.TemplateSyntaxError, \
              "%r tag requires 3 or 4 arguments" % bits[0]
    if len(bits) == 4:
        language = parser.compile_filter(bits[3])
    else:
        language = None
    return EditTranslationNode(bits[1], bits[2], language)
        
register.tag('edit_translation', do_edit_translation)


