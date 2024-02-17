from django.contrib import admin
from .models import Funcionario, Atendimento

# @admin.register(Municipio)
# class MunicipioAdmin(admin.ModelAdmin):
#     list_display = ('nome', 'contrato', 'ativo')
#     exclude = ['usuario_criador']

#     # Preenche o atributo usuario_criador com o usuário logado.
#     def save_model(self, request, obj, form, change):
#         obj.usuario_criador = request.user
#         super().save_model(request, obj, form, change)

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'usuario')
    exclude = ['usuario_criador', 'ativo']

    def save_model(self, request, obj, form, change):
        obj.usuario_criador = request.user
        super().save_model(request, obj, form, change)


    

