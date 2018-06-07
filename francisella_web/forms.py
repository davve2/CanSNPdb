from django import forms

class SubmitForm(forms.Form):
	#template_name="submission.html"
	strain = forms.CharField()
	CanSNPs = forms.CharField()
	email = forms.EmailField()