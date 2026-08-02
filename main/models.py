from django.db import models
from django.urls import reverse
from django.utils import timezone
from datetime import datetime


class Projects(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, db_index=True)
    picture = models.ImageField("picture(800x600)", upload_to="project_picture/")
    client = models.CharField(max_length=120, null=True, blank=True)
    date_created = models.DateField(default=timezone.now, null=True)
    project_url = models.URLField(null=True, blank=True)
    category = models.ForeignKey("Categories", on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_details", kwargs={"slug": self.slug})

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"


class ProjectsPictures(models.Model):
    title = models.CharField(max_length=120, default="project picture", null=True, blank=True)
    picture = models.ImageField("picture(1288x600)", upload_to="project_pictures/%Y/%m", null=True)
    project = models.ForeignKey("Projects", on_delete=models.SET_NULL, null=True, related_name="pictures")


class Categories(models.Model):
    title = models.CharField(max_length=50, null=True)
    slug = models.SlugField(max_length=50, db_index=True)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
