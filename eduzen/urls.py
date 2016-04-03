from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns,static
from django.views.generic import TemplateView
from . import settings
from django.contrib.auth.decorators import login_required
import django.views.defaults

from django.contrib import admin

urlpatterns = [
    url(r'^', include('reader.urls',namespace="reader")),
    url(r'^admin/', admin.site.urls),
    url(r'^user/',include('login.urls',namespace="login")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
admin.site.site_header = settings.ADMIN_SITE_HEADER
