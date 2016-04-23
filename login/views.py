from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.views import logout

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

# def checkLogin(request):
# 	user = request.user
# 	if user is None or not user.is_authenticated or user.is_anonymous():
# 		url = reverse('account_login')
# 	else:
# 		url = reverse('reader:mylibrary', kwargs={'pk':user.id,'user_name':user.username})
# 	return HttpResponseRedirect(url)