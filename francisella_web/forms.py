from django import forms
from django.utils import timezone
from django.forms.widgets import HiddenInput
from betterforms.multiform import MultiForm
from collections import OrderedDict
from django_countries.fields import CountryField

class UserForm(forms.Form):
    first_name= forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class' : 'CharField'}))
    last_name= forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class' : 'CharField'}))
    email= forms.EmailField()
    username= forms.CharField(max_length=20,widget=forms.TextInput(attrs={'class' : 'CharField'}))
    password= forms.CharField(max_length=100, widget=forms.PasswordInput)
    confirm_password= forms.CharField(max_length=100, widget=forms.PasswordInput)

class CanSNPForm(forms.Form):
    date=forms.DateTimeField(initial=timezone.now(),widget=HiddenInput())
    first_name= forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class' : 'CharField'}))
    last_name= forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class' : 'CharField'}))
    email= forms.EmailField()
    publication_country=CountryField(blank_label='(Select country)',max_length=100).formfield(attrs={'class' : 'CharField'}) # ,
    Select=CountryField().formfield(blank_label='(Select country)',required=False) #widget=forms.TextInput(attrs={'class' : 'CharField'}),
    countries_selected=forms.CharField(widget=forms.Textarea(attrs={'class' : 'CharField','style': 'height: 1em;'}),required=False)
    #publication_country=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class' : 'CharField'}))
    info= forms.CharField(widget=forms.Textarea(attrs={'class' : 'CharField'}),required=False)
    fasta= forms.FileField(required=False)
    


class CustomSNPForm(forms.Form):
    css_class = "custom_form"
    choises = [(x,x) for x in ["FSC200","LVS","SCHUS4"]]
    
    clade=forms.CharField(initial="B",widget=forms.TextInput(attrs={'class' : 'CharField','onChange':"updateClade()","id":"cladeField"}),required=False)
    sub_clade=forms.CharField(widget=forms.TextInput(attrs={'class' : 'CharField','onChange':"updateSubClade()","id":"subCladeField"}),required=False)
    SNP_number=forms.CharField(widget=forms.TextInput(attrs={'class' : 'ReadOnly CharField',"id":"SNPnumber","readonly":"True","title":"shows next available SNP number for selected Clade (non editable)"}),required=False)
    Ref_genome=forms.ChoiceField(choices=choises,widget=forms.Select(attrs={'class':"CharField"}),required=True)
    Ref_position=forms.CharField(initial="12445599",widget=forms.TextInput(attrs={'class' : 'CharField',"id":"position"}),required=False)

    parent=forms.CharField(widget=forms.TextInput(attrs={'class' : 'CharField'}),required=False)
    child=forms.CharField(widget=forms.TextInput(attrs={'class' : 'CharField'}),required=False)

    


class MultiCanSNPForm(MultiForm):
    form_classes = OrderedDict((
        ("SNP_base", CanSNPForm),
        ("SNP_custom", CustomSNPForm)
    ))
