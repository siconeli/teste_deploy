from django.contrib import admin
from .models import TipoAndamentoAdm, MunicipioAdm, Assunto

@admin.register(TipoAndamentoAdm)
class TipoAndamentoAdmAdmin(admin.ModelAdmin):
    list_display = ('tipo_andamento', 'ativo')
    exclude = ['usuario_criador']

    
    def save_model(self, request, obj, form, change):
        obj.usuario_criador = request.user
        super().save_model(request, obj, form, change)

@admin.register(Assunto)
class AssuntoAdmin(admin.ModelAdmin):
    list_display = ('assunto', 'ativo' )
    exclude = ['usuario_criador']

    def save_model(self, request, obj, form, change):
        obj.usuario_criador = request.user
        super().save_model(request, obj, form, change)

@admin.register(MunicipioAdm)
class MunicipioAdmAdm(admin.ModelAdmin):
    list_display = ('nome', 'tipo_contrato', 'contrato', 'brasao', 'ativo' )
    exclude = ['usuario_criador']

    # Preenche o atributo usuario_criador com o usuário logado.
    def save_model(self, request, obj, form, change):
        obj.usuario_criador = request.user
        super().save_model(request, obj, form, change)
