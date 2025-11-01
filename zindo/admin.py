from django.contrib import admin

from . import models


@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.TextBook)
class TextBookAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Sheet)
class SheetAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Record)
class RecordAdmin(admin.ModelAdmin):
    pass
