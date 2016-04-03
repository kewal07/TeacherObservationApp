from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.views import logout

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
