from django import forms
from .models import ExtendedUser
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.forms import extras
from datetime import datetime
from datetime import date
from django.conf import settings
from django.forms import widgets
from . import countryAndStateList
import os
import pymysql
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.forms.extras.widgets import SelectDateWidget
from evaluationapp.models import School

class CustomDateInput(widgets.TextInput):
	input_type = 'date'

class HorizontalRadioRenderer(forms.RadioSelect.renderer):
  def render(self):
    return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class MySignupForm(forms.Form):
	required_css_class = 'required'
	curyear = datetime.now().year
	image = forms.ImageField(required=False,label='Profile Image')
	first_name = forms.CharField(max_length=30, label='Full Name', widget=forms.TextInput(attrs={'name':'first_name','placeholder': 'First Name','autofocus': 'autofocus','id':'signup-full-name'}))
	last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last Name','name':'last_name','id':'signup-full-name'}))
	gender = forms.ChoiceField(choices=[('F','Female'), ('M','Male'), ('D','NotSay')], label='Gender',widget=forms.Select(attrs={'class':'select2 form-control'}),required=True)
	school = forms.ChoiceField([(i.id, i.school_name) for i in School.objects.all()], widget=forms.Select(attrs={'class':'select2 form-control'}),required=True)
	address = forms.CharField( max_length=1024, label="Address", widget=forms.TextInput(attrs={'placeholder': 'Address'}),required=False)
	city = forms.CharField( max_length=512, widget=forms.TextInput(attrs={'placeholder': 'City/Town'}),required=True)
	country = forms.ChoiceField([i for i in countryAndStateList.countryList], widget=forms.Select(attrs={'id':'select2_sample4', 'class':'select2 form-control'}),required=True)
	agreement = forms.BooleanField(required=False,label="")

	def __init__(self,*args,**kwargs):
		super(MySignupForm,self).__init__(*args,**kwargs)

	def signup(self, request, user):
		user.first_name = self.cleaned_data['first_name']
		user.last_name = self.cleaned_data['last_name']
		address = request.POST.get('address','')
		city=request.POST.get('city','')
		country=request.POST.get('country','')
		school = request.POST.get('school','')
		gender = request.POST.get('gender','')
		userSchool = School.objects.get(pk=int(school))
		extendeduser = ExtendedUser(user=user,address=address,city=city,country=country,imageUrl=request.FILES.get('image',''), school=userSchool, gender=gender)
		extendeduser.save()
