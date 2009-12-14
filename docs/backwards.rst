==============================
Backwards Incompatible Changes
==============================


Translation table rename
========================

In revision 98 the default name for translation tables was changed: instead of
"modeltranslation" it is now "model_translation". You don't have to rename your
tables, just upgrade to DM revision 102 or later and add a Meta class within
your translation model::

    class MyModel(models.Model):
        [...]
        class Translation(multilingual.Translation):
            my_field = ...
            class Meta:
                db_table="my_modeltranslation"

Note that this "class Meta" is inside the inner Translation class. 
