from django.shortcuts import render
from django.views.generic import View,TemplateView,FormView

from .forms import SubmitForm

class HomeView(TemplateView):
	template_name="home.html"

class WikiView(TemplateView):
	template_name="wiki.html"

class SubmitView(TemplateView):
	template_name="submission.html"

class AnalysisView(TemplateView):
	template_name="analysis.html"