"""
WSGI config for eduzen project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ['HTTPS'] = "on"
sys.path.append("/home/ubuntu/EReader_Django")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduzen.settings")

application = get_wsgi_application()
