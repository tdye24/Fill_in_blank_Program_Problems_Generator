"""
WSGI config for Fill_in_blank_Program_Problems_Generator project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Fill_in_blank_Program_Problems_Generator.settings')

application = get_wsgi_application()
