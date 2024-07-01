from django.contrib import admin

from . import models

admin.site.register(models.Project)
admin.site.register(models.File)
admin.site.register(models.Sequence)
admin.site.register(models.SequenceItem)
admin.site.register(models.Response)
