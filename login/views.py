from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.views import logout
from allauth.account.forms import ChangePasswordForm
from allauth.account.views import PasswordChangeView

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

class MyChangePasswordView(PasswordChangeView):
	def post(self,request,*args,**kwargs):
		form_class = super(MyChangePasswordView, self).get_form_class()
		form = self.get_form(form_class)
		data={}
		# print(form.save())
		if form.is_valid():
			super(MyChangePasswordView, self).form_valid(form)
		else:
			# response = self.form_invalid(form)
			# response.template_name = "login/profile.html"
			data['form_errors'] = form._errors
			return HttpResponse(json.dumps(data),
                            content_type='application/json')
		if request.is_ajax():
			return HttpResponse(json.dumps(data),
                            content_type='application/json')
		url = reverse('account_login')
		return HttpResponseRedirect(url)
		# return get_adapter().ajax_response(request, response, form=form, redirect_to=reverse('login:loggedIn', kwargs={'pk':request.user.id,'user_slug':request.user.extendeduser.user_slug}))


# def checkLogin(request):
# 	user = request.user
# 	if user is None or not user.is_authenticated or user.is_anonymous():
# 		url = reverse('account_login')
# 	else:
# 		url = reverse('reader:mylibrary', kwargs={'pk':user.id,'user_name':user.username})
# 	return HttpResponseRedirect(url)