from django.contrib import admin
from django.conf import settings
from login.models import ExtendedUser
# Register your models here.

class ExtUserAdmin(admin.ModelAdmin):
    search_fields = ('user__username', )

admin.site.register(ExtendedUser,ExtUserAdmin)
