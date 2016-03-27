from django.shortcuts import render

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
