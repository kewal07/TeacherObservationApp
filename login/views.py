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
		if form.is_valid():
			super(MyChangePasswordView, self).form_valid(form)
		else:
			data['form_errors'] = form._errors
			return HttpResponse(json.dumps(data),
                            content_type='application/json')
		if request.is_ajax():
			return HttpResponse(json.dumps(data),
                            content_type='application/json')
		url = reverse('account_login')
		return HttpResponseRedirect(url)