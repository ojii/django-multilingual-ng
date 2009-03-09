from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.forms.fields import BooleanField
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.util import ErrorDict
from django.utils.translation import ugettext as _

from multilingual.languages import *
from multilingual.utils import is_multilingual_model

def _translation_form_full_clean(self, previous_full_clean):
    """
    There is a bug in Django that causes inline forms to be
    validated even if they are marked for deletion.

    This function fixes that by disabling validation
    completely if the delete field is marked and only copying
    the absolutely required fields: PK and FK to parent.

    TODO: create a fix for Django, have it accepted into trunk and get
    rid of this monkey patch.
    
    """

    def cleaned_value(name):
        field = self.fields[name]
        val = field.widget.value_from_datadict(self.data, self.files,
                                               self.add_prefix(name))
        return field.clean(val)

    delete = cleaned_value(DELETION_FIELD_NAME)

    if delete:
        # this object is to be skipped or deleted, so only
        # construct the minimal cleaned_data
        self.cleaned_data = {'DELETE': delete,
                             'id': cleaned_value('id')}
        self._errors = ErrorDict()
    else:
        return previous_full_clean()

class TranslationInlineFormSet(BaseInlineFormSet):

    def _construct_forms(self):
        ## set the right default values for language_ids of empty (new) forms
        super(TranslationInlineFormSet, self)._construct_forms()
        
        empty_forms = []
        lang_id_list = get_language_id_list()
        lang_to_form = dict(zip(lang_id_list, [None] * len(lang_id_list)))

        for form in self.forms:
            language_id = form.initial.get('language_id')
            if language_id:
                lang_to_form[language_id] = form
            else:
                empty_forms.append(form)

        for language_id in lang_id_list:
            form = lang_to_form[language_id]
            if form is None:
                form = empty_forms.pop(0)
                form.initial['language_id'] = language_id
    
    def add_fields(self, form, index):
        super(TranslationInlineFormSet, self).add_fields(form, index)

        previous_full_clean = form.full_clean
        form.full_clean = lambda: _translation_form_full_clean(form, previous_full_clean)

class TranslationModelAdmin(admin.StackedInline):
    template = "admin/edit_inline_translations_newforms.html"
    fk_name = 'master'
    extra = get_language_count()
    max_num = get_language_count()
    formset = TranslationInlineFormSet

class ModelAdminClass(admin.ModelAdmin.__metaclass__):
    """
    A metaclass for ModelAdmin below.
    """
    
    def __new__(cls, name, bases, attrs):
        # Move prepopulated_fields somewhere where Django won't see
        # them.  We have to handle them ourselves.
        prepopulated_fields = attrs.get('prepopulated_fields', {})
        attrs['prepopulated_fields'] = {}
        attrs['_dm_prepopulated_fields'] = prepopulated_fields
        return super(ModelAdminClass, cls).__new__(cls, name, bases, attrs)

class ModelAdmin(admin.ModelAdmin):
    """
    All model admins for multilingual models must inherit this class
    instead of django.contrib.admin.ModelAdmin.
    """
    __metaclass__ = ModelAdminClass
    
    def _media(self):
        media = super(ModelAdmin, self)._media()
        if getattr(self.__class__, '_dm_prepopulated_fields', None):
            from django.conf import settings
            media.add_js(['%sjs/urlify.js' % (settings.ADMIN_MEDIA_PREFIX,)])
        return media
    media = property(_media)

    def render_change_form(self, request, context, add=False, change=False,
                           form_url='', obj=None):
        # I'm overriding render_change_form to inject information
        # about prepopulated_fields

        trans_model = self.model._meta.translation_model
        trans_fields = trans_model._meta.translated_fields
        adminform = context['adminform']
        form = adminform.form

        def field_name_to_fake_field(field_name):
            """
            Return something that looks like a form field enough to
            fool prepopulated_fields_js.html

            For field_names of real fields in self.model this actually
            returns a real form field.
            """
            try:
                field, language_id = trans_fields[field_name]
                if language_id is None:
                    language_id = get_default_language()

                # TODO: we have this mapping between language_id and
                # field id in two places -- here and in
                # edit_inline_translations_newforms.html
                # It is not DRY.
                field_idx = language_id - 1
                ret = {'auto_id': 'id_translations-%d-%s' % (field_idx, field.name)
                       }
            except:
                ret = form[field_name]
            return ret

        adminform.prepopulated_fields = [{
            'field': field_name_to_fake_field(field_name),
            'dependencies': [field_name_to_fake_field(f) for f in dependencies]
        } for field_name, dependencies in self._dm_prepopulated_fields.items()]

        return super(ModelAdmin, self).render_change_form(request, context,
                                                          add, change, form_url, obj)

def get_translation_modeladmin(cls, model):
    if hasattr(cls, 'Translation'):
        tr_cls = cls.Translation
        if not issubclass(tr_cls, TranslationModelAdmin):
            raise ValueError, ("%s.Translation must be a subclass "
                               + " of multilingual.TranslationModelAdmin.") % cls.name
    else:
        tr_cls = type("%s.Translation" % cls.__name__, (TranslationModelAdmin,), {})
    tr_cls.model = model._meta.translation_model
    return tr_cls

# TODO: multilingual_modeladmin_new should go away soon.  The code will
# be split between the ModelAdmin class, its metaclass and validation
# code.
def multilingual_modeladmin_new(cls, model, admin_site, obj=None):
    if is_multilingual_model(model):
        if cls is admin.ModelAdmin:
            # the model is being registered with the default
            # django.contrib.admin.options.ModelAdmin.  Replace it
            # with our ModelAdmin, since it is safe to assume it is a
            # simple call to admin.site.register without just model
            # passed

            # subclass it, because we need to set the inlines class
            # attribute below
            cls = type("%sAdmin" % model.__name__, (ModelAdmin,), {})

        # make sure it subclasses multilingual.ModelAdmin
        if not issubclass(cls, ModelAdmin):
            from warnings import warn
            warn("%s should be registered with a subclass of "
                 " of multilingual.ModelAdmin." % model, DeprecationWarning)
        
        # if the inlines already contain a class for the
        # translation model, use it and don't create another one
        translation_modeladmin = None
        for inline in getattr(cls, 'inlines', []):
            if inline.model == model._meta.translation_model:
                translation_modeladmin = inline

        if not translation_modeladmin:
            translation_modeladmin = get_translation_modeladmin(cls, model)
            if cls.inlines:
                cls.inlines.insert(0, translation_modeladmin)
            else:
                cls.inlines = [translation_modeladmin]
    return admin.ModelAdmin._original_new_before_dm(cls, model, admin_site, obj)

def install_multilingual_modeladmin_new():
    """
    Override ModelAdmin.__new__ to create automatic inline
    editor for multilingual models.
    """
    admin.ModelAdmin._original_new_before_dm = admin.ModelAdmin.__new__
    admin.ModelAdmin.__new__ = staticmethod(multilingual_modeladmin_new)
    
