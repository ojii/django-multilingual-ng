#####
Usage
#####

***************************************
Defining translatable fields on a Model
***************************************

Translatable fields on a model are defined using a nested class which must be a subclass of ``multilingual.translation.TranslationModel``.

An example of a multilingual news model::

    from django.db import models
    from multilingual.translation import TranslationModel

    class NewsEntry(models.Model):
        author = models.ForeignKey('auth.User')

        class Translation(TranslationModel):
            title = models.CharField(max_length=255)
            content = models.TextField()

The inner class **must** be named ``Translation``.

*****************************
Accessing translatable fields
*****************************

If you have an instance of the ``NewsEntry`` model above, you can access the translatable fields like this::

    news_entry = NewsEntry.objects.get(id=1)
    news_entry.title # the title in the current language
    news_entry.content # the content in the current language
    news_entry.author # the author

The current language is deteced the same way django detects it.
