from django.shortcuts import render
from django.views import generic
from reader.models import BooksIssued, Note, Highlight, BookMark, Book
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

# Create your views here.
class MyLibrary(generic.DetailView):
	context_object_name = 'data'

	def get_template_names(self):
		request = self.request
		template_name = 'my_library.html'
		return [template_name]

	def get_queryset(self):
		request = self.request
		user = request.user
		context = {}
		mainData = []
		userIssuedBooks = BooksIssued.objects.filter(user=user)
		if user.is_authenticated():
			context['issuedBooks'] = userIssuedBooks
		return context

def checkLogin(request):
	user = request.user
	print('*************************')
	print(user)
	print('*************************')
	if user is None or not user.is_authenticated:
		url = reverse('account_login')
	else:
		print("here")
		url = reverse('reader:mylibrary', kwargs={'pk':user.id,'user_name':user.username})
	return HttpResponseRedirect(url)
