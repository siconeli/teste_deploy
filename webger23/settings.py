"""
Django settings for webger23 project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

import os # Módulo para utilizar funcionalidades relacionadas ao sistema operacional, como manipulação de arquivos, variáveis de ambiente e muitas outras operações relacionadas ao sistema

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Utiliza em modo de Desenvolvimento
SECRET_KEY = 'django-insecure-l^j*v2e&&e@@21#+kd@5xdj7v#!e7-iwt%x(78e0=)7_2p+!%5' 

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '64e5-191-222-170-47.ngrok-free.app'] # Aqui eu coloco o código gerado pelo ngrok para acesso externo sem o "https"

# Configuração de origens confiáveis, para funcionamento do CSRF_TOKEN
CSRF_TRUSTED_ORIGINS = ['https://64e5-191-222-170-47.ngrok-free.app'] # Aqui eu coloco o código gerado pelo ngrok para acesso externo

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic', # whitenoise para modo de desenvolvimento
    'apps.core', # Aplicação core
    'apps.processo', # Aplicação Processo
    'apps.rat', # Aplicação Rat
    'django_cleanup.apps.CleanupConfig', # Excluir arquivos da pasta de uploads após editar o registro e adicionar um novo arquivo.
    'widget_tweaks', # Biblioteca Widget - Muito importante - Torna possível eu criar um formulário HTML próprio sincronizado com as Class Based Views.
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # whitenoise para modo de produção
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware', # IMPORTANTE - Comentei essa linha para que eu consigo abrir arquivos PDF em um iframe através do google chrome, pois o XframeOptions por segurança não permite, ao colocar o sistema em produção irei descomentar a linha para que a segurança se reestabeleça.

]

# ----------------------------------------------------------------------------------
# SESSIONS SETTINGS
# Configuração para usar o banco de dados para armazenar sessões
# SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# # Configuração para criptografar os dados da sessão
# SESSION_COOKIE_SECURE = True  # Defina como True se estiver usando HTTPS
# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SAMESITE = 'Strict'

# Configuração para especificar a duração da sessão (opcional)
# SESSION_COOKIE_AGE = 3600  # Tempo em segundos (por exemplo, 3600 segundos = 1 hora)
# ------------------------------------------------------------------------------------


ROOT_URLCONF = 'webger23.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'webger23.wsgi.application'

# from decouple import config

# Database - Documentação de configuração padrão para cada tipo de banco de dados
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Utilizado em modo de produção - Para utilizar o banco nativo do django - SQLite3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Utiliza em modo de Desenvolvimento - PostgreSQL pgAdmin4
# DATABASES = {
#     'default': {  
#         'ENGINE': 'django.db.backends.postgresql', 
#         'NAME': 'webger23',
#         'USER': 'postgres',
#         # 'PASSWORD': 'Clodomir753$',
#         'PASSWORD': 'abcd1590',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True # Utilizado em modo de Desenvolvimento
# USE_TZ = False # Utilizado em modo de produção


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Configuração dos arquivos estáticos: css, js, imagens
STATIC_URL = '/static/' # Usado durante o desenvolvimento
# STATIC_ROOT = str(BASE_DIR / 'staticfiles') # Usado durante a produção

# STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

#================================================================================================================
# Arquivos de Media (Para salvar os arquivos em endereço local, na mesma máquina do código) (USAR DURANTE O DESENVOLVIMENTO)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Arquivos de Media (Para salvar os arquivos em um servidor externo, acessado via IP) (USAR DURANTE A PRODUÇÃO)
# MEDIA_ROOT = ('//10.0.0.3/webger23/') # Encaminha o arquivo para o Servidor, quando é realizado um upload.
# Servidor utilizado: MyCloud EX2 Ultra
#================================================================================================================


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações de autenticação padrão de login
LOGIN_REDIRECT_URL = 'index'  # Redireciona para a url de nome 'index' após realizar o login
LOGOUT_REDIRECT_URL = 'login' # Ao fazer o logout(sair), ira direcionar para a url de nome 'login'
LOGIN_URL = 'login'  # Ao tentar acessar uma funcionalidade com permissão apenas para quem tem permissão, ira direcionar para a url de nome 'login'

# LOGGING ------------------------------

LOGGING = {
    'version': 1,
    'loggers':{
        'auditoria_erros':{ # Nome do Logger.
            'handlers':['file', ], # Lista de nome dos handlers.
            'level':'INFO'
        }
    },
    'handlers':{
        'file':{ # handler citado na lista de handlers.
            'level':'INFO',
            'class':'logging.FileHandler', # Tipo de handler "Arquivo".
            'filename': os.path.join(BASE_DIR, 'logs/processo.log'), # Ira salvar a mensagem de log no arquivo 'processo.log' dentro da pasta 'logs'.
            'formatter':'simpleRe',
        },
    },
    'formatters':{ 
        'simpleRe':{ # formatter citado no hadler 'file'
            'format':'Level: {levelname} | Data: {asctime} | Modulo: {module} | Aviso: {message}',
            'style':'{',

        }
    }
}
# -------------------------------------

# Recursos extras de Segurança do Django - Inseridos manualmente.
SECURE_HSTS_SECONDS = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'

