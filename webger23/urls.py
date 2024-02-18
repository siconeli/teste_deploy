from django.contrib import admin

from django.urls import path, include

from django.conf.urls.static import static

from django.conf import settings

urlpatterns = [
    path('central-admin/', admin.site.urls), # Admin do Django
    path('', include('core.urls')),
    path('', include('processo.urls')),
    path('', include('rat.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # Para fazer a autenticação de Login/Logout, não é preciso criar urls.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Editar a Área Administrativa do Django
admin.site.site_title = 'Cadastros' # Título da aba do navegador da tela de Login
admin.site.site_header = 'Central Administrativa' # Título da tela de Login
admin.site.index_title = 'Cadastros' # Título da página principal após o login