from django.shortcuts import render
from django.views import generic
from reader.models import BooksIssued, Note, Highlight, BookMark, Book
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect,HttpResponse, HttpResponseNotFound
import sys, os
import simplejson as json

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

	def post(self,request,*args,**kwargs):
		try:
			message = {}
			request = self.request
			user = request.user
			alreadyIssuedBooksCount = BooksIssued.objects.filter(user=user).count()
			if(alreadyIssuedBooksCount == 3):
				message['success'] = 'You already have 3 books issued. First return a book from MyLibrary to continue'
				return HttpResponse(json.dumps(message), content_type='application/json')

			bookId = int(request.POST.get('bookId',''))
			bookToIssue = Book.objects.get(pk=bookId)

			if bookToIssue:
				issuedBooks, created = BooksIssued.objects.get_or_create(user=user, book=bookToIssue)
			else:
				message['success'] = 'Error occured while issuing book'
				return HttpResponse(json.dumps(message), content_type='application/json')

			if created:
				message['success'] = 'Book is successfully issued'
				return HttpResponse(json.dumps(message), content_type='application/json')
			else:
				message['success'] = 'This book is already issued to you.'
				return HttpResponse(json.dumps(message), content_type='application/json')
		except:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
			message['success'] = 'Some error occured'
			return HttpResponse(json.dumps(message), content_type='application/json')

class ReturnBookView(generic.ListView):
	template_name = 'my_library.html'
	def get_queryset(self):
		context = {}
		return context

	def post(self,request,*args,**kwargs):
		try:
			message = {}
			request = self.request
			user = request.user
			bookId = int(request.POST.get('bookId',''))
			issuedBook = BooksIssued.objects.filter(user=user, book=bookId)

			if issuedBook:
				issuedBook.delete();
				message['success'] = 'Book returned successfully'
				return HttpResponse(json.dumps(message), content_type='application/json')
			else:
				message['success'] = 'Error in returning book'
				return HttpResponse(json.dumps(message), content_type='application/json')
		except:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
			message['success'] = 'Some error occured'
			return HttpResponse(json.dumps(message), content_type='application/json')

def getbook(request):
	message = {}
	try:
		bookId = int(request.POST.get('bookId',''))
		if bookId:
			bookToRead = Book.objects.get(pk=bookId)
			bookUrl = str(bookToRead.bookEpub)
			bookUrl = '/media/books/'+bookUrl.split('/')[-1]
			message['bookUrl'] = bookUrl
			return HttpResponse(json.dumps(message), content_type='application/json')
		else:
			message['error'] = 'Error retrieving book info.'
			return HttpResponse(json.dumps(message), content_type='application/json')
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print(' Exception occured in function %s() at line number %d of %s,\n%s:%s ' % (exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, __file__, exc_type.__name__, exc_obj))
		message['error'] = 'Some error occured'
		return HttpResponse(json.dumps(message), content_type='application/json')

def checkLogin(request):
	user = request.user
	if user is None or not user.is_authenticated:
		url = reverse('account_login')
	else:
		print("here")
		url = reverse('reader:mylibrary', kwargs={'pk':user.id,'user_name':user.username})
	return HttpResponseRedirect(url)
