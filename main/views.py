from django.shortcuts import render
from .models import Projects, Categories
from django.views.generic import ListView, DetailView, TemplateView


def get_lang(request):
    # from pprint import pprint
    # pprint(request.__dir__())
    # pprint(request.META)
    # print(f"{request.scheme}://{request.get_host()}/")
    if "/ru/" in request.path:
        lang_url = request.path.replace("ru", "en")
    else:
        lang_url = request.path.replace("en", "ru")
    return lang_url


class IndexView(ListView):
    model = Projects
    template_name = "main/index.html"
    context_object_name = "projects"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lang"] = get_lang(self.request)
        return context

    def get_categories(self):
        categories = Categories.objects.all()
        return categories


class ProjectDetail(DetailView):
    model = Projects
    # template_name = "main/portfolio-details.html"
    context_object_name = "project"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lang"] = get_lang(self.request)
        return context
