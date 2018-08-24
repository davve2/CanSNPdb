from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView,FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from francisella_web.scripts.create_tree import FrancisellaTree,get_tree,submit_SNP
from django.core import serializers
from django.http import JsonResponse
import json

from .forms import UserForm,CanSNPForm,CustomSNPForm,MultiCanSNPForm

class HomeView(TemplateView):
	template_name="home.html"

class WikiView(TemplateView):
	template_name="wiki.html"

class SubmitView(LoginRequiredMixin,FormView):
	login_url = '/login/'
	redirect_field_name = "next"
	template_name="submission.html"
	form_class=MultiCanSNPForm
	success_url = "/analysis"

	def post(self, request, *args, **kwargs):
		form = MultiCanSNPForm(request.POST)
		submit(self.request.user,**self.request.POST)
		### can I save submit object, and then reaccess and finalize after user confirmation?
		### Or is it better do do this via the database?

		if False:
			## User confirmed
			submit.upload()
			### Or simple function, confirm upload which submits from tmp db to unofficialSNPs.db
		return redirect("/processSubmission/")

class AnalysisView(TemplateView):
	template_name="analysis.html"

class ProcessView(TemplateView):
	template_name="process_submission.html"


def get_tree_data(request,**kwargs):
	data = request.POST
	res = get_tree(SNPid=request.POST["SNPid"],table=request.POST["table"],database=request.POST["database"])
	return JsonResponse(json.dumps(res),safe=False)

def databaseRequest(request,**kwargs):
	data = request.POST
	res =152

	return JsonResponse(json.dumps(res),safe=False)

def submit(user,**kwargs):
	'''Submit SNP and add to database'''
	submit = submit_SNP(user=user,database="submitted.db",table="SNP",**kwargs)
	return submit
