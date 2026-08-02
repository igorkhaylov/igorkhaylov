from django.contrib import admin
from .models import Projects, ProjectsPictures, Categories
from modeltranslation.admin import TranslationAdmin
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class ProjectsPicturesInline(admin.StackedInline):
    model = ProjectsPictures
    extra = 3


class ProjectsAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget())


@admin.register(Projects)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ("title", "category", )
    form = ProjectsAdminForm
    prepopulated_fields = {"slug": ("title", )}
    inlines = [ProjectsPicturesInline, ]

    save_on_top = True


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ("title", )
    prepopulated_fields = {"slug": ("title", )}
# admin.site.register(Categories)

