from django.shortcuts import render
from django.views import generic
from reader.models import BooksIssued, Note, Highlight, BookMark, Book
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

# Create your views here.
class MyLibrary(generic.ListView):
	context_object_name = 'data'

	def get_template_names(self):
		request = self.request
		template_name = 'my_library.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		request = self.request
		user = request.user
		context = {}
		issuedBooks = []
		userIssuedBooks = BooksIssued.objects.filter(user=user)
		for booking in userIssuedBooks:
			book = Book.objects.get(id=booking.book_id)
			issuedBooks.append(book)
		context['issuedBooks'] = issuedBooks
		return context

# Create your views here.
class CentralLibrary(generic.ListView):
	context_object_name = 'data'

	def get_template_names(self):
		request = self.request
		template_name = 'central_library.html'
		return [template_name]

	def get_queryset(self, **kwargs):
		request = self.request
		user = request.user
		context = {}
		issuedBooks = []
		bookList = Book.objects.all()
		context['books'] = [book for book in bookList]
		return context

class IssueBookView(generic.ListView):
	template_name = 'central_library.html'
	def get_queryset(self):
		context = {}
		return context

	def get(self,request,*args,**kwargs):
		user = request.user
		bookId = request.GET.get('bookId','')
		issuedBooks = UserIssuedBooks

def checkLogin(request):
	user = request.user
	if user is None or not user.is_authenticated:
		url = reverse('account_login')
	else:
		print("here")
		url = reverse('reader:mylibrary', kwargs={'pk':user.id,'user_name':user.username})
	return HttpResponseRedirect(url)
