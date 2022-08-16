from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.package)
admin.site.register(models.Subcategory)
admin.site.register(models.test)
admin.site.register(models.category)
