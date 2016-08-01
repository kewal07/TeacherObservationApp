from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import ListView,DetailView
from evaluationapp.models import Grade,School,Subject,Form, Category, FormWithCategory, FormSection, FormQuestion, Question, Choice, FormVoted, Voted, VoteText, Vote, Evaluation, EvaluationStatus, TeacherSubject, TeacherClass
from evaluationapp import evappconstants
from django.contrib.auth import login
from django.contrib.auth.models import User
from login.models import ExtendedUser
import simplejson as json
import datetime
import os,sys,linecache
from django.conf import settings
from collections import OrderedDict as SortedDict
from django.core.mail import EmailMessage,send_mail
from django.core.urlresolvers import resolve,reverse
import requests
import uuid
import base64

class TestView(ListView):
	template_name = 'evaluationapp/test.html'
	context_object_name = 'data'

	def get_queryset(self, **kwargs):
		context = {}
		context["evaluations"] = Evaluation.objects.all()
		context["nav_val"] = "Ongoing Evaluations"
		return context

class IndexView(ListView):
	context_object_name = 'data'

	def get_template_names(self):
		request = self.request
		createExtendedUser(request.user)
		if request.user.extendeduser.is_admin:
			template_name = 'evaluationapp/index.html'
		else:
			template_name = 'evaluationapp/non-admin-index.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		context = {}
		return context

class FormsHomeView(ListView):
	context_object_name = 'data'

	def get_template_names(self):
		request = self.request
		if self.request.user.extendeduser.is_admin:
			template_name = 'evaluationapp/forms-home.html'
		else:
			template_name = 'evaluationapp/404.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		context = {}
		return context

class SettingsHomeView(ListView):
	context_object_name = 'data'

	def get_template_names(self):
		template_name = 'evaluationapp/settings-home.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		context = {}
		return context

class SubjectHomeView(ListView):
	context_object_name = 'data'

	def get_template_names(self):
		template_name = 'evaluationapp/subject-home.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		context = {}
		user = self.request.user
		path = self.request.path
		if path.endswith("subjects-home"):
			subjects = Subject.objects.all()
			context["subjects"] = subjects
			context["nav_val"] = "Subjects"
		elif path.endswith("classes-home"):
			grades = Grade.objects.all()
			context["classes"] = grades
			context["nav_val"] = "Classes"
		elif path.endswith("school-home"):
			schools = School.objects.all()
			context["school"] = schools
			context["nav_val"] = "School"
		return context

class DownloadHomeView(ListView):
	context_object_name = 'data'

	def get_template_names(self):
		template_name = 'evaluationapp/download-home.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		context = {}
		context['teachers'] = ExtendedUser.objects.filter(is_admin=0)
		context['forms'] = Form.objects.filter(is_public=1)
		return context

class EvaluationEditableFormsView(ListView):
	template_name = 'evaluationapp/edit-evaluations.html'
	context_object_name = 'data'

	def get_queryset(self,**kwargs):
		context = {}
		forms = Form.objects.all()
		context['forms'] =  forms
		return context

class CreateFormView(ListView):
	template_name = 'evaluationapp/create-form.html'
	context_object_name = 'data'

	def get_queryset(self):
		context = {}
		context['categories'] = Category.objects.all()
		context['DOMAIN_URL'] = settings.DOMAIN_URL
		return context

	def post(self, request, *args, **kwargs):
		try:
			edit = False
			curtime = datetime.datetime.now();
			form_id = -1
			qExpiry = None
			if request.GET.get("fid"):
				edit = True
				form_id = int(request.GET.get("fid"))
				form = Form.objects.get(pk=request.GET.get("fid"))
			user = request.user
			post_data = request.POST
			errors = {}
			form_name = post_data.get("fullname").strip()
			form_desc = post_data.get("description").strip()
			submit_text = post_data.get("submit-text")
			fSection = post_data.get("no-of-section")
			sectionList = []
			for i in range(1, int(fSection)+1):
				sectionList.append({"sectionName":post_data.get("section"+str(i)), "sectionOrder":i})
			formError = ""
			if not form_name:
				formError += "Form Title is Required<br>"
			selectedCats = request.POST.get('category-selected','').split(",")
			if not list(filter(bool, selectedCats)):
				formError += "Please Select a category<br>"
			question_count = json.loads(post_data.get("question_count"))
			ques_list = []
			if len(question_count) < 1:
				formError += "Atleast 1 question is required<br>"
			if formError:
				errors['formError'] = formError
			for que_index in question_count:
				que = {}
				que_text = post_data.get("question-title"+str(que_index)).strip()
				que_desc = post_data.get("question-description"+str(que_index)).strip()
				que_type = post_data.get("question-type"+str(que_index)).strip()
				addComment = post_data.get("question-require-feedback"+str(que_index),False)
				mandatory = post_data.get("question-mandatory"+str(que_index),False)
				horizontalOptions = post_data.get("question-horizontal-options"+str(que_index),False)
				que['text'] = que_text
				que['desc'] = que_desc
				que['type'] = que_type
				que['addComment'] = addComment
				que['mandatory'] = mandatory
				que['horizontalOptions'] = horizontalOptions
				que['sectionName'] = post_data.get("question-section"+str(que_index)).strip()
				choices = []
				queError = ""
				min_max = {}
				if not que_text:
					queError += "Question is required.<br>"
				if que_type == "rating":
					min_value = post_data.get(que_index+"---rating---Min",0)
					max_value = post_data.get(que_index+"---rating---Max",10)
					if min_value:
						min_value = int(min_value)
					if max_value:
						max_value = int(max_value)
					min_max["min_value"] = min_value
					min_max["max_value"] = max_value
					choice_elem_id = 'question'+que_index+'choiceDiv'
					if not (min_max["min_value"] and min_max["max_value"]):
						errors[choice_elem_id] = "Min and Max value is required.<br>"
					elif min_max["min_value"] > min_max["max_value"]:
						errors[choice_elem_id] = "Min Value should be less than Max.<br>"
				elif que_type != "text":
					choice_list = json.loads(post_data.get("choice_count")).get(que_index)
					if len(choice_list) < 2:
						queError += "Atleast 2 choices are required"
					for choice_count in choice_list:
						choice_elem_id = 'questionDiv'+que_index+'choice'+str(choice_count)
						choice = post_data.getlist(choice_elem_id)[0].strip()
						choices.append(choice)
						if not choice:
							errors[choice_elem_id] = "Choice required"
					if len(choices)!=len(set(choices)):
						queError += "Please provide different choices<br>"
				if queError:
					errors["question-title"+str(que_index)] = queError
				que['choice_texts'] = choices
				que['min_max'] = min_max
				ques_list.append(que)
			if errors:
				return HttpResponse(json.dumps(errors), content_type='application/json')
			else:
				form = createForm(form_id,form_name,form_desc,curtime,user,selectedCats,submit_text,fSection)
				createFormSections(form,sectionList, edit)
				createFormQues(form,ques_list,curtime,user,edit)
			errors['success'] = True
			errors['id'] = form.id
			errors['survey_slug'] = form.form_slug
			return HttpResponse(json.dumps(errors), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class EvaluationFormEditView(DetailView):
	model = Form
	template_name = 'evaluationapp/edit-form.html'

	def get_context_data(self, **kwargs):
		context = super(EvaluationFormEditView, self).get_context_data(**kwargs)
		form = context['form']
		context['categories'] = Category.objects.all()
		context['DOMAIN_URL'] = settings.DOMAIN_URL
		form_categories = FormWithCategory.objects.filter(form=form)
		form_cat = []
		for fc in form_categories:
			form_cat.append(fc.category)
		context['form_categories'] = form_cat
		allMandatory = True
		allAC = True
		allHO = True
		for form_que in form.formquestion_set.all():
			if not form_que.mandatory:
				allMandatory = False
			if not form_que.add_comment:
				allAC = False
			if not form_que.question.horizontal_options:
				allHO = False
		context['allMandatory'] = allMandatory
		context['allAC'] = allAC
		context['allHO'] = allHO
		return context

def getCheckedValue(boolVal):
	ret = ""
	if boolVal:
		ret = "checked"
	return ret

def createForm(form_id,form_name,form_desc,curtime,user,selectedCats,submit_text,fSection):
	try:
		form = None
		if form_id > 0:
			form = Form.objects.get(pk=form_id)
			form.form_name = form_name
			form.description = form_desc
			form.thanks_msg = submit_text
			form.number_sections = fSection
		else:
			form = Form( user=user, pub_date=curtime, form_name=form_name, description=form_desc, thanks_msg=submit_text, number_sections=fSection)
		form.save()
		if form_id > 0:
			for fcat in form.formwithcategory_set.all():
				fcat.delete()
		if list(filter(bool, selectedCats)):
			for cat in selectedCats:
				if cat:
					category = Category.objects.filter(category_title=cat)[0]
					fcat,created = FormWithCategory.objects.get_or_create(form=form,category=category)
		return form
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def createFormQues(form,ques_list,curtime,user,edit):
	try:
		if edit:
			form_ques = FormQuestion.objects.filter(form=form)
			for que in form_ques:
				question = que.question
				question.delete()
				que.delete()
		for que in ques_list:
			addComment = 0
			if que['addComment']:
				addComment = 1
			mandatory = 0
			if que['mandatory']:
				mandatory = 1
			horizontalOptions = 0
			if que['horizontalOptions']:
				horizontalOptions = 1
			question = Question(user=user, created_at=curtime, question_text=que['text'], description=que['desc'], horizontal_options=horizontalOptions)
			question.save()
			for index,choice_text in enumerate(que['choice_texts']):
				choice = Choice(question=question,choice_text=choice_text)
				choice.save()
			min_value = que['min_max'].get("min_value",0)
			max_value = que['min_max'].get("max_value",10)
			formQuestionSection = None
			try:
				formQuestionSection = FormSection.objects.get(form=form, sectionName=que['sectionName'])
			except:
				formQuestionSection = None
			form_que = FormQuestion(form=form, question=question, question_type=que['type'], add_comment=addComment, mandatory=mandatory, min_value=min_value, max_value=max_value, section=formQuestionSection)
			form_que.save()
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def createFormSections(form, sectionList, edit):
	try:
		if edit:
			FormSection.objects.filter(form=form).delete()
		for section in sectionList:
			fsection = FormSection(form=form, sectionName=section['sectionName'], sectionOrder=section['sectionOrder'])
			fsection.save()
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class FormPreviewView(DetailView):
	model = Form
	def get_template_names(self):
		template_name = 'evaluationapp/form-preview.html'
		return [template_name]
	
	def get_context_data(self, **kwargs):
		context = super(FormPreviewView, self).get_context_data(**kwargs)
		user = self.request.user
		path = self.request.path
		form_id = int(path.split("/")[-3])

		context['questions']=[]
		sections = FormSection.objects.filter(form_id=form_id).order_by('sectionOrder')
		questions_section_dict = SortedDict()
		questions_section_dict['Common'] = []
		for section in sections:
			questions_section_dict[section.sectionName] = []
		for i,x in enumerate(FormQuestion.objects.filter(form_id=form_id)):
			tempSectionName = ''
			if x.section:
				tempSectionName = x.section.sectionName
			else:
				tempSectionName = None
			question_dict = {"question":x.question,"type":x.question_type, "addComment":x.add_comment, "mandatory":x.mandatory, "min_value":x.min_value, "max_value":x.max_value,"horizontalOptions":x.question.horizontal_options,"section_name":tempSectionName}
			question_dict['user_already_voted'] = False
			question_user_vote = []
			if tempSectionName:
				questions_section_dict[tempSectionName].append(question_dict)
			else:
				questions_section_dict['Common'].append(question_dict)
			context['questions'].append(question_dict)
		if(not questions_section_dict['Common']):
			questions_section_dict.pop('Common',None)
		context['questions_section_dict'] = questions_section_dict		
		context['DOMAIN_URL'] = settings.DOMAIN_URL
		context['no_of_sections'] = len(questions_section_dict)
		return context


class EvaluationFormVoteView(DetailView):
	model = Form

	def get_template_names(self):
		request = self.request
		template_name = 'evaluationapp/evaluation-form-vote.html'
		path = request.path
		ev_id = path.split("/")[-1]
		evaluation = None
		try:
			evaluation = Evaluation.objects.get(pk=ev_id)
		except:
			pass
		
		if FormVoted.objects.filter(evaluation_id = evaluation):
			template_name = 'evaluationapp/evaluation-form-result.html'
		return [template_name]

	def get_context_data(self, **kwargs):
		context = super(EvaluationFormVoteView, self).get_context_data(**kwargs)
		user = self.request.user
		path = self.request.path
		ev_id = path.split("/")[-1]
		evaluation = None
		try:
			evaluation = Evaluation.objects.get(pk=ev_id)
			context["ev_status"] = EvaluationStatus.objects.get(evaluation_id=evaluation).evaluation_status_id.status_state
			context['evaluation'] = evaluation
		except:
			pass
		user_already_voted = False
		evaluatee = evaluation.evaluatee
		evaluateeSchool = evaluatee.extendeduser.school
		context['subject'] = TeacherSubject.objects.filter(evaluatee=evaluatee)
		context['class'] = TeacherClass.objects.filter(teacher=evaluatee)
		formVoted = FormVoted.objects.filter(evaluation_id = evaluation)
		if formVoted:
			user_already_voted = True
		context['user_already_voted'] = user_already_voted
		if user.is_authenticated():
			createExtendedUser(user)
		
		if user_already_voted:
			formVoted = formVoted[0]
			context['subject'] = formVoted.subject.subject_name
			context['class'] = formVoted.grade.grade_name + ' ' + formVoted.section

		context['questions']=[]
		sections = FormSection.objects.filter(form_id=context['form'].id).order_by('sectionOrder')
		questions_section_dict = SortedDict()
		questions_section_dict['Class Information'] = []
		questions_section_dict['Common'] = []
		for section in sections:
			questions_section_dict[section.sectionName] = []
		for i,x in enumerate(FormQuestion.objects.filter(form_id=context['form'].id)):
			tempSectionName = ''
			if x.section:
				tempSectionName = x.section.sectionName
			else:
				tempSectionName = None
			question_dict = {"question":x.question,"type":x.question_type, "addComment":x.add_comment, "mandatory":x.mandatory, "min_value":x.min_value, "max_value":x.max_value,"horizontalOptions":x.question.horizontal_options,"section_name":tempSectionName}
			question_dict['user_already_voted'] = False
			question_user_vote = []
			if user.is_authenticated():
				question_user_vote = Voted.objects.filter(question=x.question, evaluation=evaluation)
				if question_user_vote:
					question_dict['user_already_voted'] = True
					if x.question_type == "text":
						question_dict['answer'] = VoteText.objects.filter(question_id=x.question.id, evaluation=evaluation)[0].answer_text
					elif x.question_type == "rating":
						myrate = int(float(VoteText.objects.filter(question_id=x.question.id, evaluation=evaluation)[0].answer_text))
						question_dict["from_val"] = myrate
					else:
						choices = Vote.objects.filter(evaluation=evaluation).values_list('choice',flat=True)
						question_dict["choices"] = choices
				if x.add_comment:
					voteText = VoteText.objects.filter(question_id=x.question.id, evaluation=evaluation)
					if voteText:
						question_dict['answer'] = voteText[0].answer_text
			if tempSectionName:
				questions_section_dict[tempSectionName].append(question_dict)
			else:
				questions_section_dict['Common'].append(question_dict)
			context['questions'].append(question_dict)
		if(not questions_section_dict['Common']):
			questions_section_dict.pop('Common',None)
		context['questions_section_dict'] = questions_section_dict
		if path.startswith('/view-evaluation'):
			context["view_ev"] = True
			context["ac_re"] = False
			if user.extendeduser.is_admin:
				context["archive"] = True
				if EvaluationStatus.objects.filter(evaluation_id=evaluation, evaluation_status_id=evappconstants.getEvStatus("completed")):
					context["archive"] = False
			if user_already_voted and EvaluationStatus.objects.filter(evaluation_id=evaluation, evaluation_status_id=evappconstants.getEvStatus("submitted")):
				context["ac_re"] = True			
		context['DOMAIN_URL'] = settings.DOMAIN_URL
		context['no_of_sections'] = len(questions_section_dict)
		return context

	def post(self, request, *args, **kwargs):
		try:
			path = request.path
			ev_id = path.split("/")[-1]
			evaluation = None
			try:
				evaluation = Evaluation.objects.get(pk=ev_id)
			except:
				pass
			user = request.user
			post_data = request.POST
			form_id = int(post_data.get("survey-id"))
			subjectOfEvaluation = post_data.get('subject-of-evaluation')
			classOfEvaluation = post_data.get('class-of-evaluation').split('---')[0]
			sectionOfEvaluation = post_data.get('class-of-evaluation').split('---')[1]
			form_voted = None
			form_questions = FormQuestion.objects.filter(form_id = form_id)
			votes_list = []
			errors = {}
			total_que = len(form_questions)
			for form_question in form_questions:
				vote = {}
				question_type = form_question.question_type
				question = form_question.question
				question_id = question.id
				question_id_str = str(question_id)
				mandatory = form_question.mandatory
				vote["id"] = question_id
				vote["type"] = question_type
				answer = ""
				choices = []
				if question_type == "text":
					answer = post_data.get("choice"+question_id_str,"").strip()
				elif question_type == "rating":
					answer = post_data.get("range"+question_id_str,"").strip()
				elif question_type == "radio":
					choice = post_data.get("choice"+question_id_str,"").strip()
					choices.append(choice)
					answer = post_data.get("choice"+question_id_str+"Comment","").strip()
				elif question_type == "checkbox":
					choice = post_data.getlist("choice"+question_id_str,[])
					for v in choice:
						choices.append(v)
				choices = list(filter(None, choices))
				if mandatory:
					if question_type in ["radio","checkbox"]:
						if not choices:
							errors[question_id_str] = "Select Choice"
					elif not answer:
						errors[question_id_str] = "Enter Answer"
				vote["answer"] = answer
				vote["choices"] = choices
				votes_list.append(vote)
			if not errors:
				errors["success"] = "Successfull"
				saveVotes(user,form_id,votes_list,evaluation, subjectOfEvaluation, classOfEvaluation, sectionOfEvaluation)
			return HttpResponse(json.dumps(errors),content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def createExtendedUser(user):
	if not user.is_authenticated():
		pass
	elif hasattr(user,'extendeduser'):
		pass
	elif user.socialaccount_set.all():
		social_set = user.socialaccount_set.all()[0]
		if not (ExtendedUser.objects.filter(user_id = user.id)):
			if social_set.provider == 'facebook':
				facebook_data = social_set.extra_data
				img_url =  "https://graph.facebook.com/{}/picture?width=140&&height=140".format(facebook_data.get('id',''))
				gender_data = facebook_data.get('gender','')[0].upper()
				birth_day = facebook_data.get('birthday','2002-01-01')
				extendedUser = ExtendedUser(user=user, imageUrl = img_url, birthDay = birth_day,gender=gender_data)
				extendedUser.save()
			if social_set.provider == 'google':
				google_data = social_set.extra_data
				img_url = google_data.get('picture')
				if 'gender' in google_data :
					gender_data = google_data.get('gender','')[0].upper()
				else:
					gender_data = 'D'
				extendedUser = ExtendedUser(user=user, imageUrl = img_url, gender=gender_data)
				extendedUser.save()
	else:
		extendedUser = ExtendedUser(user=user)
		extendedUser.save()

def saveVotes(user,form_id,votes_list,evaluation, subjectOfEvaluation, classOfEvaluation, sectionOfEvaluation):
	try:
		user_voted = 0
		subject = Subject.objects.get(pk=subjectOfEvaluation)
		grade = Grade.objects.get(pk=classOfEvaluation)
		for vote in votes_list:
			if vote["type"] in ["text","rating"]:
				if vote["answer"]:
					votetext = VoteText(user=user, question_id=vote["id"], answer_text=vote["answer"], evaluation=evaluation)
					votetext.save()
					voted = Voted(user=user, question_id=vote["id"], evaluation=evaluation)
					voted.save()
					user_voted += 1
			elif vote["type"] in ["radio","checkbox"]:
				if vote["choices"]:
					user_voted += 1
					for choice_id in vote["choices"]:
						choice = Choice.objects.get(pk=int(choice_id))
						uvote = Vote(user=user, choice=choice, evaluation=evaluation)
						uvote.save()
						voted,created = Voted.objects.get_or_create(user=user, question_id=vote["id"], evaluation=evaluation)
				if vote["answer"]:
					votetext = VoteText(user=user, question_id=vote["id"], answer_text=vote["answer"], evaluation=evaluation)
					votetext.save()
		voted = FormVoted(user=user, form_id=form_id, form_question_count=len(votes_list), user_answer_count=user_voted, evaluation=evaluation, subject=subject, grade=grade, section=sectionOfEvaluation)
		voted.save()
		ev_status = EvaluationStatus.objects.filter(evaluation_id=evaluation, evaluation_status_id=evappconstants.getEvStatus("ongoing"))[0]
		ev_status.evaluation_status_id = evappconstants.getEvStatus("submitted")
		ev_status.save()
		evaluation.completed_on = datetime.datetime.now()
		evaluation.save()
	except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class EvaluationFormsStateView(DetailView):
	model = Form
	template_name = 'evaluationapp/index.html'

	def get_context_data(self, **kwargs):
		context = super(EvaluationFormsStateView, self).get_context_data(**kwargs)
		form = context['form']
		form.is_active = not form.is_active
		form.save()
		return HttpResponse(json.dumps({}), content_type='application/json')

class EvauationHomeView(ListView):
	template_name = 'evaluationapp/evaluation-home.html'
	context_object_name = 'data'

	def get_queryset(self, **kwargs):
		context = {}
		return context

class AssignEvaluationView(ListView):
	template_name = 'evaluationapp/assign-evaluation.html'
	context_object_name = 'data'

	def get_queryset(self, **kwargs):
		context = {}
		teachers = ExtendedUser.objects.filter(is_admin = 0)
		context['teachers'] = teachers
		forms = Form.objects.filter(is_active = 1, is_public =1)
		context['forms'] = forms
		return context

	def post(self,request,*args,**kwargs):
		try:
			post_data = request.POST
			errors = {}
			form = Form.objects.get(pk=post_data.get("selected-form"))
			evaluator = User.objects.get(pk=post_data.get("selected-evaluator"))
			evaluatee = User.objects.get(pk=post_data.get("selected-evaluatee"))
			evaluation_name = evaluatee.username +" evaluated by "+evaluator.username+" on "+form.form_name
			scheduled_at = None
			last_day = None
			if post_data.get("scheduled"):
				scheduled_at = datetime.datetime.strptime(post_data.get("scheduled"), "%d-%m-%Y")
			if post_data.get("lastday"):
				last_day = datetime.datetime.strptime(post_data.get("lastday"), "%d-%m-%Y")
			is_peer = post_data.get("ispeer",False)
			is_surprised = post_data.get("issurprised",False)
			tab3error = ""
			if evaluatee == evaluator:
				tab3error += "Evaluator & Evaluatee cannot be the same person"
			if Evaluation.objects.filter(evaluation_name=evaluation_name):
				tab3error += "<br> Evaluation already assigned"
			if tab3error:
				errors["tab3"] = tab3error
			if errors:
				return HttpResponse(json.dumps(errors), content_type='application/json')
			else:
				evaluation = Evaluation(evaluation_name=evaluation_name, evaluation_form=form, evaluatee=evaluatee, evaluator=evaluator, scheduled_at=scheduled_at, last_day=last_day, is_peer=is_peer, is_surprised=is_surprised)
				evaluation.save()
				ev_status = EvaluationStatus(evaluation_id=evaluation, evaluation_status_id=evappconstants.getEvStatus("ongoing"))
				ev_status.save()
				sendMails("evaluationremider", {"id": evaluation.id})
				sendMails("evaluatee", {"id": evaluation.id})
			errors['success'] = True
			errors['id'] = form.id
			errors['survey_slug'] = form.form_slug
			return HttpResponse(json.dumps(errors), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class EvaluationListView(ListView):
	template_name = 'evaluationapp/evaluation-list.html'
	context_object_name = 'data'

	def get_queryset(self, **kwargs):
		context = {}
		path = self.request.path
		user = self.request.user
		voted_evaluations = FormVoted.objects.values_list('evaluation_id', flat=True)
		voted_evaluations = list(filter(bool, voted_evaluations))
		completed_evaluations_list = []
		reviewed_status = [evappconstants.getEvStatus("accepted"), evappconstants.getEvStatus("reviewed"), evappconstants.getEvStatus("rejected")]
		completed_status = [evappconstants.getEvStatus("completed")]
		completed_evaluations = EvaluationStatus.objects.filter(evaluation_status_id__in=completed_status).values_list('evaluation_id', flat=True)
		ce = Evaluation.objects.filter(id__in=completed_evaluations).values_list('id', flat=True)
		completed_evaluations_list = ce
		if path.endswith("evaluation-ongoing"):
			context["evaluations"] = Evaluation.objects.exclude(id__in=voted_evaluations)
			context["nav_val"] = "Ongoing Evaluations"
		elif path.endswith("evaluation-submitted"):
			context["evaluations"] = Evaluation.objects.filter(id__in=voted_evaluations)
			context["nav_val"] = "Submitted Evaluations"
		elif path.endswith("evaluation-reviewed"):
			reviewed_evaluations = EvaluationStatus.objects.filter(evaluation_status_id__in=reviewed_status).values_list('evaluation_id', flat=True)
			context["evaluations"] = Evaluation.objects.filter(id__in=reviewed_evaluations)
			context["nav_val"] = "Reviewd Evaluations"
		elif path.endswith("evaluation-completed"):
			completed_evaluations = EvaluationStatus.objects.filter(evaluation_status_id__in=completed_status).values_list('evaluation_id', flat=True)
			ce = Evaluation.objects.filter(id__in=completed_evaluations)
			context["evaluations"] = ce
			completed_evaluations_list = list(filter(bool, ce))
			context["nav_val"] = "Completed Evaluations"
		elif path.endswith("evaluation-under-me"):
			activeForms = Form.objects.filter(is_active=1)
			activeForms = list(activeForms)
			context["evaluations"] = Evaluation.objects.filter(evaluator_id= user).filter(evaluation_form_id__in=activeForms)			
			for evaluation in context["evaluations"]:
				status = EvaluationStatus.objects.get(evaluation_id=evaluation)
				if status.evaluation_status_id.status_id == 1 and evaluation.scheduled_at.replace(tzinfo=None) < datetime.datetime.now().replace(tzinfo=None):
					evaluation.dateCrossed = True
				else:
					evaluation.dateCrossed = False
			context["nav_val"] = "Evaluations Under Me"
			evaluations_list_under_me = Evaluation.objects.filter(evaluator_id= user).values_list('id', flat=True)
			context["status"] = EvaluationStatus.objects.filter(evaluation_id__in=evaluations_list_under_me)
		elif path.endswith("my-evaluations"):
			context["evaluations"] = Evaluation.objects.filter(evaluatee_id=user).filter(evaluation_form__is_active=1)
			for evaluation in context["evaluations"]:
				status = EvaluationStatus.objects.get(evaluation_id=evaluation)
				if status.evaluation_status_id.status_id == 1 and evaluation.scheduled_at.replace(tzinfo=None) < datetime.datetime.now().replace(tzinfo=None):
					evaluation.dateCrossed = True
				else:
					evaluation.dateCrossed = False
			context["nav_val"] = "My Evaluations"
			my_evals = Evaluation.objects.filter(evaluatee_id= user).values_list('id', flat=True)
			context["status"] = EvaluationStatus.objects.filter(evaluation_id__in=my_evals)
		elif path.endswith("evaluation-review"):
			evr = Evaluation.objects.exclude(id__in=completed_evaluations_list)
			for evaluation in evr:
				status = EvaluationStatus.objects.get(evaluation_id=evaluation)
				if status.evaluation_status_id.status_id == 1 and evaluation.scheduled_at.replace(tzinfo=None) < datetime.datetime.now().replace(tzinfo=None):
					evaluation.dateCrossed = True
				else:
					evaluation.dateCrossed = False
			context["evaluations"] = evr
			context["status"] = EvaluationStatus.objects.filter(evaluation_id__in=evr)
			context["nav_val"] = "Review Evaluations"
		elif path.endswith("evaluation-archive"):
			completed_evaluations = EvaluationStatus.objects.filter(evaluation_status_id__in=completed_status).values_list('evaluation_id', flat=True)
			ce = Evaluation.objects.filter(id__in=completed_evaluations)
			context["evaluations"] = ce
			context["nav_val"] = "Archived Evaluations"
		return context

class SendMail(ListView):
	template_name = 'evaluationapp/evaluation-list.html'
	context_object_name = 'data'

	def get_queryset(self, **kwargs):
		context = {}
		path = self.request.path
		get_data = self.request.GET
		action = get_data.get("action","")
		sendMails(action, get_data)
		return context

def sendMails(action, data_dict):
	isSend = True
	if action == "evaluationremider":
		subject = "Please Finish Evaluation"
		evaluation = Evaluation.objects.get(id=data_dict.get("id"))
		offset = data_dict.get("offset",0)
		offset = int(offset)
		lastDayTime = evaluation.last_day - datetime.timedelta(minutes=offset)
		evaluation_url = settings.DOMAIN_URL + reverse('evaluationapp:evaluation_form_vote', kwargs={'pk':evaluation.evaluation_form.id, 'form_slug':evaluation.evaluation_form.form_slug, 'evaluation_id':evaluation.id})
		message = "Hi %s,\n\nPlease complete the evaluation for %s using %s before %s"%(evaluation.evaluator.first_name,evaluation.evaluatee.first_name,evaluation_url,lastDayTime)
		to_mail = ['kewal07@gmail.com',evaluation.evaluator.email]
	elif action == "evaluatee":
		subject = "You are being evaluated"
		evaluation = Evaluation.objects.get(id=data_dict.get("id"))
		if evaluation.is_surprised:
			isSend = False
		message = "Hi %s,\n\nYou will be evaluated by %s"%(evaluation.evaluatee.first_name,evaluation.evaluator.first_name)
		to_mail = ['kewal07@gmail.com',evaluation.evaluatee.email]
	if isSend:
		send_mail(subject, message, 'eduzenreader@gmail.com',to_mail, fail_silently=False)

class ViewEvaluationView(DetailView):
	model = Form
	template_name = 'evaluationapp/view-evaluation.html'
	context_object_name = 'data'

	def get_queryset(self, **kwargs):
		context = {}
		path = self.request.path
		get_data = self.request.GET
		evaluation_id = int(get_data.get("eid",""))
		form_id = int(get_data.get("fid",""))
		return context

class AcceptRejectView(DetailView):
	model = Evaluation
	template_name = 'evaluationapp/evaluation-form-vote.html'

	def get_context_data(self, **kwargs):
		context = super(AcceptRejectView, self).get_context_data(**kwargs)
		get_data = self.request.GET
		action = get_data.get("action","")
		evaluation = context["evaluation"]
		if action == "accept":
			ev_status = EvaluationStatus.objects.filter(evaluation_id=evaluation, evaluation_status_id=evappconstants.getEvStatus("submitted"))[0]
			ev_status.evaluation_status_id = evappconstants.getEvStatus("accepted")
			ev_status.save()
		if action == "reject":
			ev_status = EvaluationStatus.objects.filter(evaluation_id=evaluation, evaluation_status_id=evappconstants.getEvStatus("submitted"))[0]
			ev_status.evaluation_status_id = evappconstants.getEvStatus("rejected")
			ev_status.save()
		if action == "archive":
			ev_status = EvaluationStatus.objects.filter(evaluation_id=evaluation)[0]
			ev_status.evaluation_status_id = evappconstants.getEvStatus("completed")
			ev_status.save()
		return context

import xlwt

normal_style = xlwt.easyxf(
	"""
	font:name Verdana
	"""
)

border_style = xlwt.easyxf(
	"""
	font:name Verdana;
	border: top thin, right thin, bottom thin, left thin;
	align: vert centre, horiz left;
	"""
)

def excel_view(request):
	if not request.user.is_authenticated():
		errors['notloggedin'] = "User not logged In"
		return HttpResponseNotFound(errors,content_type="application/json")
	post_data = request.GET
	export_type = post_data.get("export_type","")
	teacher_id = int(post_data.get("teacher-select",-1))
	form_id = int(post_data.get("form-select",-1))
	response = HttpResponse(content_type='application/ms-excel')
	wb = xlwt.Workbook()
	ws0 = wb.add_sheet('Definitions', cell_overwrite_ok=True)
	ws1 = wb.add_sheet('Raw Data', cell_overwrite_ok=True)
	errors = {}
	try:
		if export_type == "evaluation_per_teacher_per_form":
			teacher = User.objects.get(pk=teacher_id)
			form = None
			evaluation = None
			ev_status = ""
			try:
				form = Form.objects.get(pk=form_id)
				evaluation = Evaluation.objects.get(evaluation_form=form, evaluatee=teacher)
				ev_status = EvaluationStatus.objects.filter(evaluation_id=evaluation)[0].evaluation_status_id.status_state
			except:
				return HttpResponseNotFound("This Evaluation has not been done yet")
			# raw data sheet 
			ws1.write(0,0,"Evaluator",normal_style)
			ws1.write(0,1,"Evaluatee",normal_style)
			ws1.write(0,2,"Evaluation Form",normal_style)
			ws1.write(0,3,"Evaluation Name",normal_style)
			ws1.write(0,4,"Status",normal_style)
			i = 1
			j = 1
			form_question_list = FormQuestion.objects.filter(form_id = form_id)
			# write to the description sheet
			write_on_sheet1(ws0, form_question_list)
			voted_list = FormVoted.objects.filter(evaluation = evaluation)
			for voted in voted_list:
				vote_user = voted.user
				addVal = 0
				ws1.write(i,0,vote_user.first_name+" "+vote_user.last_name+" ( "+vote_user.username+" )",normal_style)
				ws1.write(i,1,teacher.first_name+" "+teacher.last_name+" ( "+teacher.username+" )",normal_style)
				ws1.write(i,2,form.form_name,normal_style)
				ws1.write(i,3,evaluation.evaluation_name,normal_style)
				ws1.write(i,4,ev_status,normal_style)
				j = 5
				for index,form_question in enumerate(form_question_list):
					question = form_question.question
					question_type = form_question.question_type
					excel_text = ""
					choice_list = Choice.objects.filter(question_id=question.id)
					excel_text = "Q"+str(index+1)
					answer_text = ""
					answer_texts = []
					excel_texts = []
					if question_type in ["text", "rating"]:
						vote_text = VoteText.objects.filter(user_id=vote_user.id,question_id=question.id)
						if vote_text:
							answer_text = vote_text[0].answer_text
					elif question_type == "radio":
						for c_index,choice in enumerate(choice_list):
							vote = Vote.objects.filter(user_id=vote_user.id,choice=choice)
							if vote:
								answer_text = str(c_index+1)
						if answer_text:
							answer_texts.append(answer_text)
						else:
							answer_texts.append(0)
						excel_texts.append(excel_text)
					elif question_type == "checkbox":
						for c_index,choice in enumerate(choice_list):
							excel_text = "Q"+str(index+1)+"_"+str(c_index+1)
							answer_text = 0
							vote = Vote.objects.filter(user_id=vote_user.id,choice=choice)
							if vote:
								answer_text = 1
							answer_texts.append(answer_text)
							excel_texts.append(excel_text)
					if form_question.add_comment and question_type not in ["text", "rating"]:
						excel_texts.append("Q"+str(index+1)+"_Comments")
						additionalComment = VoteText.objects.filter(user=voted.user, question=question)
						if additionalComment:
							answer_texts.append(additionalComment[0].answer_text)
						else:
							answer_texts.append("No Comments")
					if answer_texts:
						for ans_index,answer in enumerate(answer_texts):
							write_result_into_excel(ws1,excel_texts[ans_index],answer,i,j+index+ans_index+addVal)
						addVal += ans_index
					else:
						write_result_into_excel(ws1,excel_text,answer_text,i,j+index+addVal)
				i += 1		
			fname = "%s %s_Evaluated_on_%s.xls"%(teacher.first_name,teacher.last_name,form.form_name)
			response['Content-Disposition'] = 'attachment; filename=%s' % fname
			wb.save(response)
			return response
		errors['notfound'] = "No data provided"
		return HttpResponseNotFound("<h1>Evaluation not found</h1>",content_type="application/json")
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
		errors['notfound'] = "Form provided not found"
		return HttpResponseNotFound("Evaluation not found",content_type="application/json")

def write_result_into_excel(ws1,excel_text,answer_text,i,j):
	ws1.write(0,j,excel_text,normal_style)
	ws1.write(i,j,answer_text,normal_style)
	return i,j

def write_on_sheet1(ws0, form_question_list):
	try:
		ws0.col(0).width = 25*256
		i = 0
		ws0.write(i,0,"Single Select Questions Have 1 as lowest & 5 as highest Rating",normal_style)
		i += 1
		ws0.write(i,0,"Multi Select Questions are displayed as Q_Choice No & its respective rating",normal_style)
		i += 2
		j = 0
		for index,form_que in enumerate(form_question_list):
			ws0.write(i,1,"Q"+str(index+1),normal_style)
			ws0.write(i,2,form_que.question.question_text,normal_style)
			i += 1
			if form_que.question_type in ["radio", "checkbox"]:
				for c_index,choice in enumerate(form_que.question.choice_set.all()):
					if form_que.question_type == "radio":
						ws0.write(i,3,c_index+1,normal_style)
					elif form_que.question_type == "checkbox":
						ws0.write(i,3,"Q"+str(index+1)+"_"+str(c_index+1),normal_style)
					ws0.write(i,4,choice.choice_text,normal_style)
					i += 1
				i += 1
	except Exception as e:
		exc_type, exc_obj, tb = sys.exc_info()
		f = tb.tb_frame
		lineno = tb.tb_lineno
		filename = f.f_code.co_filename
		linecache.checkcache(filename)
		line = linecache.getline(filename, lineno, f.f_globals)
		print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def get_token_from_code(auth_code, redirect_uri):
	scopes = ['openid', 'https://outlook.office.com/mail.read']
	authority = 'https://login.microsoftonline.com'
	token_url = '{0}{1}'.format(authority, '/common/oauth2/v2.0/token')
	post_data = {
		'grant_type': 'authorization_code',
        	'code': auth_code,
        	'redirect_uri': redirect_uri,
        	'scope': ' '.join(str(i) for i in scopes),
        	'client_id': 'ac92782f-c87a-48e5-9b4d-9ba250c8b11b',
        	'client_secret': 'FJb8apcLnH98+bpg8uPWbqOOur7qF4LZ8oyQDoSZhk4=',
        	'state': '12345'
    	}
	r = requests.post(token_url, data = post_data)
	try:
		return r.json()
	except:
		return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)

def get_user_email_from_id_token(id_token):
	token_parts = id_token.split('.')
	encoded_token = token_parts[1]

	leftovers = len(encoded_token)%4
	if leftovers == 2:
		encoded_token += '=='
	elif leftovers == 3:
		encoded_token += '='

	# URL-safe base64 decode the token parts
	decoded = base64.urlsafe_b64decode(encoded_token.encode('utf-8')).decode('utf-8')
	jwt = json.loads(decoded)
	return jwt['preffered_username']

def gettoken(request):
	auth_code = request.GET['code']
	redirect_uri = request.build_absolute_uri(reverse('evaluationapp:gettoken'))
	token = get_token_from_code(auth_code, redirect_uri)
	print(token)
	access_token = token['access_token']
	user_email = get_user_email_from_id_token(token['id_token'])
	print(user_email)
	request.session['access_token'] = access_token
	request.session['user_email'] = user_email 
	try:
		print(r.json())
		return r.json()
	except:
		return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)
