"""
WSGI config for webger23 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# from dj_static import Cling, MediaCling # Usado durante a Produção.

os.environ.setdefault['DJANGO_SETTINGS_MODULE'] = 'webger23.settings'

application = get_wsgi_application()
 

