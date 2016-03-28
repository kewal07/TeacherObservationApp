from django.conf.urls import patterns, include, url
from login import views
from reader import views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$',views.checkLogin,name='checklogin'),
	url(r'^mylibrary/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.MyLibrary.as_view()),name='mylibrary'),
    url(r'^centrallibrary/(?P<pk>\d+)/(?P<user_name>[\w\-]+)$',login_required(views.CentralLibrary.as_view()),name='centrallibrary'),
	#url(r'^(?P<pk>\d+)/(?P<user_slug>[\w\-]+)/editprofile$',login_required(views.LoggedInView.as_view()),name='editprofile'),
	#url(r'^editprofile$',login_required(views.EditProfileView.as_view()),name='edit_profile'),
	#url(r'^logout$',views.logout_view,name="logout"),
	#url(r'^changepassword$',login_required(views.MyChangePasswordView.as_view()),name="change_password"),
	# url(r'^/detail$',views.DetailView.as_view(),name='detail'),
]
