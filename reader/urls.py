from django.conf.urls import patterns, include, url
from login import views
from reader import views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$',views.checkLogin,name='checklogin'),
	url(r'^mylibrary/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.MyLibrary.as_view()),name='mylibrary'),
    url(r'^centrallibrary/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.CentralLibrary.as_view()),name='centrallibrary'),
    url(r'^myprofile/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.MyProfile.as_view()),name='myprofile'),
	url(r'^issuebook$',login_required(views.IssueBookView.as_view()),name='issuebook'),
	url(r'^returnbook$',login_required(views.ReturnBookView.as_view()),name='returnbook'),
	url(r'^getbookurl$',login_required(views.getbook),name='getbook'),
    url(r'^getbookmarks$',login_required(views.getbookmarks),name='getbookmarks'),
    url(r'^gethighlights$',login_required(views.getHighlights),name='gethighlights'),
	url(r'^getnotes$',login_required(views.getNotes),name='getNotes'),
	url(r'^savenotes$',login_required(views.saveNotes),name='saveNotes'),
    url(r'^savebookmark$',login_required(views.saveBookmark),name='savebookmark'),
    url(r'^savehighlights$',login_required(views.saveHighlights),name='savehighlights'),
]
