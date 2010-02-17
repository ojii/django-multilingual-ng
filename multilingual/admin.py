"""Admin suppor for inlines

Peter Cicman, Divio GmbH, 2008
"""
from django.utils.text import capfirst, get_text_list
from django.contrib.admin.util import flatten_fieldsets
from django.http import HttpResponseRedirect
from django.utils.encoding import force_unicode

import re
from copy import deepcopy
from django.conf import settings
from django import forms
from django.contrib import admin
from django.forms.util import ErrorList, ValidationError
from django.forms.models import BaseInlineFormSet, ModelFormMetaclass
from django.utils.translation import ugettext as _

MULTILINGUAL_PREFIX = '_ml__trans_'
MULTILINGUAL_INLINE_PREFIX = '_ml__inline_trans_'

class MultilungualInlineModelForm(forms.ModelForm):
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        """Just full up intitial values for ml fields
        """
        super(MultilungualInlineModelForm, self).__init__(data, files, auto_id, prefix,
                                                    initial, error_class, label_suffix,
                                                    empty_permitted, instance)
        
        # read data for existing object, and set them as initial
        for name, db_field in get_translated_fields(self.instance):
            full_name = '%s%s' % (MULTILINGUAL_INLINE_PREFIX, name)
            if full_name in self.fields:
                self.fields[full_name].initial = getattr(self.instance, name, '')


class MultilingualInlineFormSet(BaseInlineFormSet):
    def get_queryset(self):
        if not hasattr(self, '_queryset'):
            if self.queryset is not None:
                qs = self.queryset
            else:
                qs = self.model._default_manager.get_query_set()

            # If the queryset isn't already ordered we need to add an
            # artificial ordering here to make sure that all formsets
            # constructed from this queryset have the same form order.
            if not qs.ordered:
                qs = qs.order_by(self.model._meta.pk.name)

            if self.max_num > 0:
                self._queryset = qs[:self.max_num]
            else:
                self._queryset = qs
            if hasattr(self, 'use_language'):
                self._queryset  = qs.filter(translations__language_code=self.use_language)
        return self._queryset

    def save_new(self, form, commit=True):
        """NOTE: save_new method is completely overridden here, there's no
        other way to pretend double save otherwise. Just assign translated data
        to object  
        """
        kwargs = {self.fk.get_attname(): self.instance.pk}
        new_obj = self.model(**kwargs)
        self._prepare_multilingual_object(new_obj, form)
        return forms.save_instance(form, new_obj, exclude=[self._pk_field.name], commit=commit)
    
    def save_existing(self, form, instance, commit=True):
        """NOTE: save_new method is completely overridden here, there's no
        other way to pretend double save otherwise. Just assign translated data
        to object  
        """
        self._prepare_multilingual_object(instance, form)
        return forms.save_instance(form, instance, exclude=[self._pk_field.name], commit=commit)
    
    def _prepare_multilingual_object(self, obj, form):
        for name in form.cleaned_data:
            m = re.match(r'^%s(?P<field_name>.*)$' % MULTILINGUAL_INLINE_PREFIX, name)
            if m:
                setattr(obj, m.groupdict()['field_name'], form.cleaned_data[name])
      
      
class MultilingualInlineAdmin(admin.TabularInline):
    formset = MultilingualInlineFormSet
    form = MultilungualInlineModelForm
    
    template = 'admin/multilingual/edit_inline/tabular.html'
    
    # css class added to inline box
    inline_css_class = None
    
    use_language = None
    #TODO: add some nice template
    
    def __init__(self, parent_model, admin_site):
        super(MultilingualInlineAdmin, self).__init__(parent_model, admin_site)
        if hasattr(self, 'use_fields'):
            # go around admin fields structure validation
            self.fields = self.use_fields
        
    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super(MultilingualInlineAdmin, self).get_formset(request, obj=None, **kwargs)
        FormSet.use_language = self.use_language
        for name, field in get_translated_fields(self.model, self.use_language):
            FormSet.form.base_fields['%s%s' % (MULTILINGUAL_INLINE_PREFIX, name)] = self.formfield_for_dbfield(field)
        return FormSet
    
    
class MultilingualModelAdminForm(forms.ModelForm):
    # for rendering / saving multilingual fields connecte to model, takes place
    # when admin per language is ussed
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        """Just full up intitial values for ml fields
        """
        super(MultilingualModelAdminForm, self).__init__(data, files, auto_id, prefix,
                                                    initial, error_class, label_suffix,
                                                    empty_permitted, instance)
        # read data for existing object, and set them as initial
        for name in self.ml_fields:
            self.fields[name].initial = getattr(self.instance, "%s_%s" % (name, self.use_language), '')
    
    def clean(self):
        cleaned_data = super(MultilingualModelAdminForm, self).clean()
        self.validate_ml_unique()
        return cleaned_data
    
    def validate_ml_unique(self):
        form_errors = []
        
        for check in self.instance._meta.translation_model._meta.unique_together[:]:
            lookup_kwargs = {'language_code': self.use_language}
            for field_name in check:
                #local_name = "%s_%s" % (field_name, self.use_language)
                if self.cleaned_data.get(field_name) is not None:
                    lookup_kwargs[field_name] = self.cleaned_data.get(field_name) 
            
            if len(check) == 2 and 'master' in check and 'language_code' in check:
                continue
                
            qs = self.instance._meta.translation_model.objects.filter(**lookup_kwargs)
            if self.instance.pk is not None:
                qs = qs.exclude(master=self.instance.pk)
            
            if qs.count():
                model_name = capfirst(self.instance._meta.verbose_name)
                field_labels = []
                for field_name in check:
                    if field_name == "language_code":
                        field_labels.append(_("language"))
                    elif field_name == "master":
                        continue
                    else:
                        field_labels.append(self.instance._meta.translation_model._meta.get_field_by_name(field_name)[0].verbose_name)
                field_labels = get_text_list(field_labels, _('and'))
                form_errors.append(
                    _(u"%(model_name)s with this %(field_label)s already exists.") % \
                    {'model_name': unicode(model_name),
                     'field_label': unicode(field_labels)}
                )
        if form_errors:
            # Raise the unique together errors since they are considered
            # form-wide.
            raise ValidationError(form_errors)
                
    
    def save(self, commit=True):
        self._prepare_multilingual_object(self.instance, self)
        return super(MultilingualModelAdminForm, self).save(commit)    
        
        
    def _prepare_multilingual_object(self, obj, form):
        for name in self.ml_fields:
            setattr(obj, "%s_%s" % (name, self.use_language), form.cleaned_data[name])



class ModelAdmin(admin.ModelAdmin):
    
    # use special template to render tabs for languages on top
    change_form_template = "admin/multilingual/change_form.html"
    
    form = MultilingualModelAdminForm
    
    _multilingual_model_admin = True
    
    use_language = None
    
    def __init__(self, model, admin_site):
        if hasattr(self, 'use_fieldsets'):
            # go around admin fieldset structure validation
            self.fieldsets = self.use_fieldsets
        if hasattr(self, 'use_prepopulated_fields'):
            # go around admin fieldset structure validation
            self.prepopulated_fields = self.use_prepopulated_fields
        super(ModelAdmin, self).__init__(model, admin_site)
    
    
    
    def get_form(self, request, obj=None, **kwargs):    
        self.use_language = request.GET.get('lang', request.GET.get('language', settings.LANGUAGES[settings.DEFAULT_LANGUAGE][0]))
        # assign language to inlines, so they now how to render
        for inline in self.inline_instances:
            if isinstance(inline, MultilingualInlineAdmin):
                inline.use_language = self.use_language
        
        Form = super(ModelAdmin, self).get_form(request, obj, **kwargs)
        
        Form.ml_fields = {}
        for name, field in get_default_translated_fields(self.model):
            if not field.editable:
                continue
            form_field = self.formfield_for_dbfield(field)
            local_name = "%s_%s" % (name, self.use_language)
            Form.ml_fields[name] = form_field
            Form.base_fields[name] = form_field
            Form.use_language = self.use_language
        return Form
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        # add context variables
        context.update({
            'current_language_index': self.use_language,
            'current_language_code': self.use_language
        })
        return super(ModelAdmin, self).render_change_form(request, context, add, change, form_url, obj)
    
                
    def response_change(self, request, obj):
        # because save & continue - so it shows the same language
        if request.POST.has_key("_continue"):
            opts = obj._meta
            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            lang, path = request.GET.get('lang', None), request.path
            if lang:
                lang = "lang=%s" % lang
            if request.REQUEST.has_key('_popup'):
                path += "?_popup=1" + "&%s" % lang
            else:
                path += "?%s" % lang
            return HttpResponseRedirect(path)
        return super(ModelAdmin, self).response_change(request, obj)

    
    class Media:
        css = {
            'all': ('%smultilingual/admin/css/style.css' % settings.MEDIA_URL,)
        }
    

def get_translated_fields(model, language=None):
    meta = model._meta
    if not hasattr(meta, 'translated_fields'):
        meta = meta.translation_model._meta
    # returns all the translatable fields, except of the default ones
    if not language:
        for name, (field, non_default) in meta.translated_fields.items():
            if non_default: 
                yield name, field
    else:
        # if language is defined return fields in the same order, like they are defined in the 
        # translation class
        for field in meta.fields:
            if field.primary_key:
                continue
            name = field.name + "_%s" % language
            field = meta.translated_fields.get(name, None)
            if field:
                yield name, field[0]
        

def get_default_translated_fields(model):
    for name, (field, non_default) in model._meta.translation_model._meta.translated_fields.items():
        if not non_default:
            yield name, field
