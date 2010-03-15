import math
import StringIO
import tokenize

from django import template
from django import forms
from django.template import Node, NodeList, Template, Context, resolve_variable
from django.template.loader import get_template, render_to_string
from django.conf import settings
from django.utils.html import escape
from multilingual.languages import (
    get_default_language,
    get_language_code_list,
    get_language_name,
    get_language_bidi,
    get_language_idx
)
from multilingual.utils import GLL

register = template.Library()


def language_name(language_code):
    """
    Return the name of the language with id=language_code
    """
    return get_language_name(language_code)


def language_bidi(language_code):
    """
    Return whether the language with id=language_code is written right-to-left.
    """
    return get_language_bidi(language_code)

def language_for_id(language_id):
    return get_language_idx(language_for_id)


class EditTranslationNode(template.Node):
    def __init__(self, form_name, field_name, language=None):
        self.form_name = form_name
        self.field_name = field_name
        self.language = language

    def render(self, context):
        form = resolve_variable(self.form_name, context)
        model = form._meta.model
        trans_model = model._meta.translation_model
        if self.language:
            language_code = self.language.resolve(context)
        else:
            language_code = get_default_language()
        real_name = "%s.%s.%s.%s" % (self.form_name,
                                     trans_model._meta.object_name.lower(),
                                     get_language_idx(language_code),
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


def reorder_translation_formset_by_language_code(inline_admin_form):
    """
    Shuffle the forms in the formset of multilingual model in the
    order of their language_ids.
    """
    lang_to_form = dict([(form.form.initial['language_id'], form)
                         for form in inline_admin_form])
    return [lang_to_form[language_code] for language_code in
        get_language_code_list()]
    
class GLLNode(template.Node):
    def __init__(self, language_code, nodelist):
        self.language_code = language_code
        self.nodelist = nodelist
    
    def render(self, context):
        if self.language_code[0] == self.language_code[-1] and self.language_code[0] in ('"',"'"):
            language_code = self.language_code[1:-1]
        else:
            language_code = template.Variable(self.language_code).resolve(context) 
        GLL.lock(language_code)
        output = self.nodelist.render(context)
        GLL.release()
        return output
    
def gll(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError("gll takes exactly one argument")
    language_code = bits[1]
    nodelist = parser.parse(('endgll',))
    parser.delete_first_token()
    return GLLNode(language_code, nodelist)

register.filter(language_for_id)
register.filter(language_name)
register.filter(language_bidi)
register.tag('edit_translation', do_edit_translation)
register.filter(reorder_translation_formset_by_language_code)
register.tag('gll', gll)