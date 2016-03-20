from django.shortcuts import render
from django.views import generic

# Create your views here.
class IndexView(generic.DetailView):
	context_object_name = 'data'
	# paginate_by = 50

	def get_template_names(self):
		request = self.request
		template_name = 'polls/index.html'
		if request.path.endswith('category') and not request.GET.get('category'):
			template_name = 'polls/categories.html'
		return [template_name]

	def get_queryset(self):
		createExtendedUser(self.request.user)
		request = self.request
		user = request.user
		context = {}
		mainData = []
		latest_questions = []
		curtime = timezone.now()
		global_location = ""
		country_list =[]
		if user.is_authenticated() and request.path == reverse('polls:mypolls', kwargs={'pk': user.id, 'user_name':user.extendeduser.user_slug}):
			if request.GET.get('tab') == 'mycategories':
				category_questions = []
				if user.extendeduser.categories:
					user_categories_list = list(map(int,user.extendeduser.categories.split(',')))
					user_categories = Category.objects.filter(pk__in=user_categories_list)
					que_cat_list = QuestionWithCategory.objects.filter(category__in=user_categories)
					category_questions = [x.question for x in que_cat_list if x.question.privatePoll == 0 and x.question.home_visible == 1]
					latest_questions.extend(category_questions)
			elif request.GET.get('tab') == 'followed':
				followed_questions = [x.question for x in Subscriber.objects.filter(user=user)]
				latest_questions.extend(followed_questions)
			elif request.GET.get('tab') == 'voted':
				voted_questions = [x.question for x in Voted.objects.filter(user=user)]
				latest_questions.extend(voted_questions)
			elif request.GET.get('tab') == 'mypolls' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
				asked_polls = Question.objects.filter(user=user)
				latest_questions.extend(asked_polls)
			if latest_questions:
				latest_questions = list(OrderedDict.fromkeys(latest_questions))
				latest_questions.sort(key=lambda x: x.pub_date, reverse=True)
		else:
			latest_questions = Question.objects.filter(privatePoll=0,home_visible=1).order_by('-pub_date')[:50]
			latest_questions = list(OrderedDict.fromkeys(latest_questions))
			if request.GET.get('tab') == 'mostvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=True)
			elif request.GET.get('tab') == 'latest' or request.GET.get('tab','NoneGiven') == 'NoneGiven':
				latest_questions = latest_questions
			elif request.GET.get('tab') == 'leastvoted':
				latest_questions.sort(key=lambda x: x.voted_set.count()+VoteApi.objects.filter(question=x).exclude(age__isnull=True).exclude(gender__isnull=True).exclude(profession__isnull=True).count(), reverse=False)
			elif request.GET.get('tab') == 'withexpiry':
				toexpire_polls = [x for x in latest_questions if x.expiry and x.expiry > curtime]
				expired_polls = [x for x in latest_questions if x.expiry and x.expiry <= curtime]
				toexpire_polls.sort(key=lambda x: x.expiry, reverse=False)
				expired_polls.sort(key=lambda x: x.expiry, reverse=True)
				latest_questions = []
				if toexpire_polls:
					latest_questions.extend(toexpire_polls)
				if expired_polls:
					latest_questions.extend(expired_polls)
		subscribed_questions = []
		if user.is_authenticated():
			subscribed_questions = Subscriber.objects.filter(user=request.user)
		sub_que = []
		for sub in subscribed_questions:
			sub_que.append(sub.question.id)
		if country_list:
			latest_questions = [x for x in latest_questions if x.user.extendeduser and x.user.extendeduser.country in country_list ]
		for mainquestion in latest_questions:
			mainData.append(get_index_question_detail(mainquestion,user,sub_que,curtime))
		particleList = Particle.objects.order_by('-pub_date')
		primer = Particle.objects.filter(is_prime=1).latest()
		context['primer'] = primer
		featuredParticles = []
		for x in particleList:
			if x.is_featured == 1 and x != primer:
				featuredParticles.append(x)
				if len(featuredParticles) == 4:
					break
		featuredParticles1 = featuredParticles[:2]
		featuredParticles2 = featuredParticles[2:]
		context['featuredParticles'] = featuredParticles
		context['featuredParticles1'] = featuredParticles1
		context['featuredParticles2'] = featuredParticles2
		context['data'] = mainData
		return context
