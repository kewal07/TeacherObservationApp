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

	def __str__(self):
		return self.grade_name

class SchoolGradeSection(models.Model):
	school = models.ForeignKey(School)
	grade = models.ForeignKey(Grade)
	section = models.CharField(max_length=10)
	students_count = models.IntegerField(blank=True,null=True,default=0)
	number_emirati =  models.IntegerField(blank=True,null=True,default=0)
	number_nonemirati = models.IntegerField(blank=True,null=True,default=0)
	number_boys = models.IntegerField(blank=True,null=True,default=0)
	number_girls = models.IntegerField(blank=True,null=True,default=0)
	def __str__(self):
		return self.school.school_name+"_"+self.grade.grade_name+"_"+self.section

class Subject(models.Model):
	subject_id = models.IntegerField(blank=True,null=True,default=0)
	subject_name = models.CharField(max_length=512,blank=True,null=True)
	grade = models.ForeignKey(Grade)

	def __str__(self):
		return self.subject_name + " " + self.grade.grade_name

class TeacherClassSubject(models.Model):
	teacher = models.ForeignKey(settings.AUTH_USER_MODEL)
	school_grade_section = models.ForeignKey(SchoolGradeSection)
	subject = models.ForeignKey(Subject)
	def __str__(self):
		return self.teacher.first_name+"_"+ self.school_grade_section.school.school_name+"_"+self.school_grade_section.grade.grade_name+"_"+self.school_grade_section.section+"_"+ self.subject.subject_name

class GradeSchemes(models.Model):
	scheme_name = models.CharField(max_length=64)
	school = models.ForeignKey(School)
	teacher = models.ForeignKey(settings.AUTH_USER_MODEL)
	created_on = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	def __str__(self):
		return self.school.school_name+'__'+self.teacher.first_name+'__'+self.scheme_name

class GradesRange(models.Model):
	schemes = models.ForeignKey(GradeSchemes)
	grade = models.CharField(max_length=50)
	maxscore = models.IntegerField(default=100)
	minscore = models.IntegerField(default=100)
	def __str__(self):
		return self.grade+'__'+str(self.maxscore)+'__'+str(self.minscore)

class Form(models.Model):
	form_name = models.CharField(max_length=200)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	pub_date = models.DateTimeField('Date Published')
	description = models.CharField(max_length=400,null=True,blank=True)
	form_slug = models.SlugField(null=True,blank=True)
	created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	thanks_msg = models.CharField(max_length=400,null=True,blank=True, default="Thank You for Completing the Assessment!!!")
	grading_scheme = models.ForeignKey(GradeSchemes, null=True, blank=True, default = None)
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
	question_text      = models.CharField(max_length=200)
	user               = models.ForeignKey(settings.AUTH_USER_MODEL)
	description        = models.CharField(max_length=400,null=True,blank=True)
	que_slug           = models.SlugField(null=True,blank=True)
	created_at         = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	horizontal_options = models.BooleanField(default=1)
	na                 = models.BooleanField(default=0)
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
	question      = models.ForeignKey(Question)
	choice_text   = models.CharField(max_length=200)
	choice_weight = models.IntegerField(default=1)
	choice_value  = models.FloatField(default=1.0)
	na            = models.BooleanField(default=0)
	def __str__(self):
		return self.choice_text

class FormQuestion(models.Model):
	form          = models.ForeignKey(Form)
	question      = models.ForeignKey(Question)
	question_type = models.CharField(max_length=20)
	add_comment   = models.BooleanField(default=0)
	mandatory     = models.BooleanField(default=0)
	min_value     = models.IntegerField(default=0)
	max_value     = models.IntegerField(default=10)
	weight        = models.IntegerField(default=1)
	value         = models.FloatField(default=1.0)
	section       = models.ForeignKey(FormSection,null=True,default=None)
	def __str__(self):
		return self.form.form_name+"_"+self.question.question_text+"_"+self.question_type

class Status(models.Model):
	status_id = models.IntegerField(default=0)
	status_state = models.CharField(max_length=20)
	def __str__(self):
		return str(self.id)+" : "+str(self.status_id)+" : "+self.status_state

class Evaluation(models.Model):
	evaluation_name = models.CharField(max_length=512,blank=True,null=True)
	evaluation_form = models.ForeignKey(Form)
	evaluatee = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='user_evaluatee')
	evaluator = models.ForeignKey(settings.AUTH_USER_MODEL,blank=True,null=True,related_name='user_evaluator')
	created_at = models.DateTimeField(auto_now_add=True)
	scheduled_at = models.DateTimeField(blank=True, null=True, auto_now_add=False)
	completed_on = models.DateTimeField(blank=True, null=True, auto_now_add=False)
	last_day = models.DateTimeField(blank=True, null=True, auto_now_add=False)
	is_peer = models.BooleanField(default=1)
	is_external = models.BooleanField(default=0)
	is_surprised = models.BooleanField(default=0)
	external_evaluator = models.ForeignKey(ExternalEvaluator,blank=True,null=True)
	evaluatee_feedback = models.CharField(max_length=512,blank=True,null=True)
	status = models.ForeignKey(Status)
	score = models.FloatField(default=1.0)
	grade = models.CharField(max_length=64,blank=True,null=True)
	def __str__(self):
		return self.evaluation_name

class Vote(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	question = models.ForeignKey(Question, null=True, blank=True, default = None)
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

class FormVoted(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	form = models.ForeignKey(Form)
	created_at = models.DateTimeField(auto_now_add=True)
	form_question_count = models.IntegerField(blank=True,null=True,default=0)
	user_answer_count = models.IntegerField(blank=True,null=True,default=0)
	evaluation = models.ForeignKey(Evaluation,blank=True,null=True)
	subject = models.ForeignKey(Subject,blank=True,null=True)
	grade_section = models.ForeignKey(SchoolGradeSection,blank=True,null=True)
	full_lesson_observation = models.BooleanField(default=0)
	def __str__(self):
		return self.form.form_name+" : "+self.user.username
	def save(self, *args, **kwargs):
		super(FormVoted, self).save(*args, **kwargs)

class EvaluationTargets(models.Model):
	school = models.ForeignKey(School)
	teacher = models.ForeignKey(settings.AUTH_USER_MODEL)
	form = models.ForeignKey(Form)
	target = models.IntegerField(blank=True,null=True,default=0)
	month = models.CharField(blank=False,null=False,default='October', max_length=25)
	year = models.IntegerField(blank=True,null=True,default=0)
	status = models.CharField(max_length=255)
	def __str__(self):
		return "Target of "+ str(self.target)+" evaluations assigned to "+self.teacher.first_name+" of "+self.school.school_name+" ( "+str(self.start_date)+" - "+str(self.end_date)+")" 
