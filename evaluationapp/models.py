import datetime
from django.db import models
from django.utils import timezone
from django.conf import settings
import os,sys,linecache
from django.template.defaultfilters import slugify
import hashlib
import hmac
from datetime import date
from django.core.urlresolvers import resolve,reverse
# Create your models here.

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	filename = "profilepic%s.%s" % (instance.user_pk, ext)
	folder_day = date.today()
	profilePath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'profile'+os.sep+str(folder_day)))
	return os.path.join(profilePath,filename)


class ExternalEvaluator(models.Model):
	external_evaluator_name = models.CharField(max_length=255)
	external_evaluator_designation = models.CharField(max_length=255)
	external_evaluator_organisation = models.CharField(max_length=255)	
	external_evaluator_bio = models.CharField(max_length=1024,blank=True,null=True)
	external_evaluator_picUrl = models.ImageField(upload_to=get_file_path,blank=True,null=True)
	
	def __str__(self):
		return self.external_evaluator_name 

	def get_profile_pic_name(self):
		return self.external_evaluator_picUrl.path.split(os.sep)[-1]

	def get_folder_day(self):
		folder_day = ""
		try:
			day = self.external_evaluator_picUrl.path.split(os.sep)[-2]
			folder_day = str(date(int(day.split("-")[0]),int(day.split("-")[1]),int(day.split("-")[2])))
		except:
			pass
		return folder_day

	def get_profile_pic_url(self):
		default_pic_url = "/static/login/images/defaultAvatar.png"
		if self.external_evaluator_picUrl:
			external_evaluator_picUrl = self.external_evaluator_picUrl.path
			if external_evaluator_picUrl.find("https:"+os.sep) != -1:
				return external_evaluator_picUrl.split('media')[1][1:]
			elif external_evaluator_picUrl.find("http:"+os.sep) != -1:
				return external_evaluator_picUrl.split('media')[1][1:]
			else:
				return "/media/profile/"+self.get_folder_day()+os.sep+self.get_profile_pic_name()
		return default_pic_url

class School(models.Model):
	school_name = models.CharField(max_length=512,blank=True,null=True)
	number_students = models.IntegerField(blank=True,null=True,default=0)
	number_teachers = models.IntegerField(blank=True,null=True,default=0)
	number_boys = models.IntegerField(blank=True,null=True,default=0)
	number_girls = models.IntegerField(blank=True,null=True,default=0)
	number_emirati =  models.IntegerField(blank=True,null=True,default=0)
	number_nonemirati = models.IntegerField(blank=True,null=True,default=0)

	def __str__(self):
		return self.school_name

class Grade(models.Model):
	grade_id = models.IntegerField(blank=True,null=True,default=0)
	grade_name = models.CharField(max_length=512,blank=True,null=True)
	students_count = models.IntegerField(blank=True,null=True,default=0)
	number_emirati =  models.IntegerField(blank=True,null=True,default=0)
	number_nonemirati = models.IntegerField(blank=True,null=True,default=0)
	number_boys = models.IntegerField(blank=True,null=True,default=0)
	number_girls = models.IntegerField(blank=True,null=True,default=0)
	school = models.ForeignKey(School,blank=True,null=True)
	grade_section = models.CharField(max_length=10,blank=True,null=True)

	def __str__(self):
		return self.grade_name + " " + self.grade_section

class Subject(models.Model):
	subject_id = models.IntegerField(blank=True,null=True,default=0)
	subject_name = models.CharField(max_length=512,blank=True,null=True)
	grade = models.ForeignKey(Grade)

	def __str__(self):
		return self.subject_name + " " + self.grade.grade_name

class Form(models.Model):
	form_name = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	pub_date = models.DateTimeField('Date Published')
	description = models.CharField(max_length=400,null=True,blank=True)
	form_slug = models.SlugField(null=True,blank=True)
	created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	thanks_msg = models.CharField(max_length=400,null=True,blank=True, default="Thank You for Completing the Assessment!!!")
	number_sections = models.IntegerField(blank=True,null=True,default=0)
	is_active = models.BooleanField(default=1)
	is_public = models.BooleanField(default=0)

	def __str__(self):
		return self.form_name

	def save(self, *args, **kwargs):
		if not self.form_slug:
			qText = self.form_name
			short_q_text = qText[:50]
			if not short_q_text.strip():
				short_q_text = None
			qslug = slugify(short_q_text)
			if not qslug and not qslug.strip():
				qslug = None
			self.form_slug = qslug
		super(Form, self).save(*args, **kwargs)

class FormSection(models.Model):
	sectionName = models.CharField(max_length=64)
	sectionOrder = models.IntegerField()
	form = models.ForeignKey(Form)
	def __str__(self):
		return self.sectionName+"---"+str(self.sectionOrder)

class Evaluation(models.Model):
	evaluation_name = models.CharField(max_length=512,blank=True,null=True)
	evaluation_form = models.ForeignKey(Form)
	evaluatee = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='user_evaluatee')
	evaluator = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name='user_evaluator')
	created_at = models.DateTimeField(auto_now_add=True)
	scheduled_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	completed_on = models.DateTimeField(blank=True, null=True, auto_now_add=False)
	last_day = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	is_peer = models.BooleanField(default=1)
	is_external = models.BooleanField(default=0)
	is_surprised = models.BooleanField(default=0)
	external_evaluator = models.ForeignKey(ExternalEvaluator,blank=True,null=True)
	def __str__(self):
		return self.evaluation_name

class TeacherSubject(models.Model):
	evaluatee = models.ForeignKey(settings.AUTH_USER_MODEL)
	subject = models.ForeignKey(Subject)
	def __str__(self):
		return self.evaluatee.first_name+ " " + self.subject.subject_name

class TeacherClass(models.Model):
	teacher = models.ForeignKey(settings.AUTH_USER_MODEL)
	grade = models.ForeignKey(Grade)
	def __str__(self):
		return str(self.teacher.first_name) + " " + str(self.grade.grade_name) + " " + str(self.grade.grade_section)

class Status(models.Model):
	status_id = models.IntegerField(default=0)
	status_state = models.CharField(max_length=20)
	def __str__(self):
		return str(self.id)+" : "+str(self.status_id)+" : "+self.status_state

class EvaluationStatus(models.Model):
	evaluation_id = models.ForeignKey(Evaluation)
	evaluation_status_id = models.ForeignKey(Status)

class Category(models.Model):
	category_title = models.CharField(max_length=50)
	def __str__(self):
		return self.category_title

class FormWithCategory(models.Model):
	form = models.ForeignKey(Form)
	category = models.ForeignKey(Category)
	def __str__(self):
		return self.form.form_name+" : "+self.category.category_title
	def save(self, *args, **kwargs):
		super(FormWithCategory, self).save(*args, **kwargs)

class Question(models.Model):
	question_text = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	description = models.CharField(max_length=400,null=True,blank=True)
	que_slug = models.SlugField(null=True,blank=True)
	created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	horizontal_options = models.BooleanField(default=1)

	def __str__(self):
		return self.question_text

	def iseditable(self, request_user):
		editable = False
		if request_user.is_superuser:
			editable = True
		elif request_user == self.user and self.voted_set.count() < 1 :
			editable = True
		return editable

	def save(self, *args, **kwargs):
		qText = self.question_text
		if not self.que_slug:
			short_q_text = qText[:50]
			if not short_q_text.strip():
				short_q_text = None
			qslug = slugify(short_q_text)
			if not qslug and not qslug.strip():
				qslug = None
			self.que_slug = qslug
		super(Question, self).save(*args, **kwargs)

class Choice(models.Model):
	question = models.ForeignKey(Question)
	choice_text = models.CharField(max_length=200)
	def __str__(self):
		return self.choice_text

class Vote(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	choice = models.ForeignKey(Choice)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	evaluation = models.ForeignKey(Evaluation,blank=True,null=True)
	def __str__(self):
		return self.choice.choice_text+" : "+self.user.username

class Voted(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	created_at = models.DateTimeField(auto_now_add=True)
	evaluation = models.ForeignKey(Evaluation,blank=True,null=True)
	def __str__(self):
		return self.question.question_text+" : "+self.user.username

class VoteText(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question)
	answer_text = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True,null=True)
	evaluation = models.ForeignKey(Evaluation,blank=True,null=True)
	def __str__(self):
		return self.answer_text

class FormQuestion(models.Model):
	form = models.ForeignKey(Form)
	question = models.ForeignKey(Question)
	question_type = models.CharField(max_length=20)
	add_comment = models.BooleanField(default=0)
	mandatory = models.BooleanField(default=0)
	min_value  = models.IntegerField(default=0)
	max_value = models.IntegerField(default=10)
	section = models.ForeignKey(FormSection,null=True,default=None)
	def __str__(self):
		return self.form.form_name+"_"+self.question.question_text+"_"+self.question_type

class FormVoted(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	form = models.ForeignKey(Form)
	created_at = models.DateTimeField(auto_now_add=True)
	form_question_count = models.IntegerField(blank=True,null=True,default=0)
	user_answer_count = models.IntegerField(blank=True,null=True,default=0)
	evaluation = models.ForeignKey(Evaluation,blank=True,null=True)
	subject = models.ForeignKey(Subject,blank=True,null=True)
	grade = models.ForeignKey(Grade,blank=True,null=True)
	section = models.CharField(max_length=20)
	full_lesson_observation = models.BooleanField(default=0)
	def __str__(self):
		return self.form.form_name+" : "+self.user.username
	def save(self, *args, **kwargs):
		super(FormVoted, self).save(*args, **kwargs)