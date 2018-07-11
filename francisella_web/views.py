from django.shortcuts import render
from django.views.generic import View,TemplateView,FormView
from francisella_web.scripts.create_tree import FrancisellaTree,get_tree
from django.core import serializers
from django.http import JsonResponse
import json

from .forms import SubmitForm

class HomeView(TemplateView):
	template_name="home.html"

class WikiView(TemplateView):
	template_name="wiki.html"

class SubmitView(TemplateView):
	template_name="submission.html"

class AnalysisView(TemplateView):
	template_name="analysis.html"

def get_tree_data(request,**kwargs):
	data = request.POST
	res = get_tree(SNPid=request.POST["SNPid"],table=request.POST["table"],database=request.POST["database"])
	return JsonResponse(json.dumps(res),safe=False)