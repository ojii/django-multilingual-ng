from django.contrib import admin
from multilingual.languages import *

class TranslationModelAdmin(admin.StackedInline):
    template = "admin/edit_inline_translations_newforms.html"
    fk_name = 'master'
    extra = get_language_count()
    max_num = get_language_count()

class ModelAdminClass(admin.ModelAdmin.__metaclass__):
    def __new__(cls, name, bases, attrs):
        # Move prepopulated_fields somewhere where Django won't see
        # them.  We have to handle them ourselves.
        prepopulated_fields = attrs.get('prepopulated_fields')
        if prepopulated_fields:
            attrs['_dm_prepopulated_fields'] = prepopulated_fields
            attrs['prepopulated_fields'] = {}
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


def is_multilingual_model(model):
    return hasattr(model._meta, 'translation_model')

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
            raise ValueError, ("%s must be registered with a subclass of "
                               + " of multilingual.ModelAdmin.") % model
        
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
    admin.ModelAdmin._original_new_before_dm = ModelAdmin.__new__
    admin.ModelAdmin.__new__ = staticmethod(multilingual_modeladmin_new)
    
