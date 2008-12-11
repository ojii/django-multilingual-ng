from django.db import models
import multilingual

class Category(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Translation(multilingual.Translation):
        name = models.CharField(max_length=250)

class OtherModel(models.Model):
    name = models.CharField(max_length=250)
