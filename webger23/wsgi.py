"""
WSGI config for webger23 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Defina a variável de ambiente DJANGO_SETTINGS_MODULE para o módulo de configurações do seu projeto Django.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webger23.settings')

# Obtém a aplicação WSGI do Django.
application = get_wsgi_application()
