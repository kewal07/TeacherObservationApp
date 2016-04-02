from django.conf.urls import patterns, include, url
from login import views
from reader import views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$',views.checkLogin,name='checklogin'),
	url(r'^mylibrary/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.MyLibrary.as_view()),name='mylibrary'),
    url(r'^centrallibrary/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.CentralLibrary.as_view()),name='centrallibrary'),
	url(r'^issuebook$',login_required(views.IssueBookView.as_view()),name='issuebook'),
	url(r'^returnbook$',login_required(views.ReturnBookView.as_view()),name='returnbook'),
	url(r'^getbookurl$',login_required(views.getbook),name='getbook'),
    url(r'^getbookmarks$',login_required(views.getbookmarks),name='getbookmarks'),
	url(r'^getnotes$',login_required(views.getNotes),name='getNotes'),
	# url(r'^/detail$',views.DetailView.as_view(),name='detail'),
]
