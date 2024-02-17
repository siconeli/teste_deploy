from typing import Any
from django.shortcuts import render
from .models import Atendimento, Funcionario
from apps.processo.models import MunicipioAdm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Q

###### VIEW ######
class AtendimentoView(TemplateView):
    template_name = 'atendimento/views/atendimento_view.html'

###### CREATE ######
class AtendimentoCreate(CreateView):
    model = Atendimento
    template_name = 'atendimento/creates/atendimento_create.html'
    fields = ['municipio', 'data', 'cliente', 'descricao']
    success_url = reverse_lazy('atendimento-create')

    def form_valid(self, form):
        """ Função Bilt-in do Django que possibilita realizar alterações nos dados de um formulário válido, antes de ser salvo no banco de dados. No uso atual, eu utilizei para preencher o atributo 'usuario_criador' com o usuário logado que realizou o envio do formulário."""
        try:
            # Se não existir funcionário vinculado ao id do usuário logado, o sistema irá pular para a exceção e retornar a mensagem de erro, pois não quero que seja possível criar um atendimento sem o cadastro de funcionário.
            usuario_logado = self.request.user
            funcionario = Funcionario.objects.get(usuario_id=usuario_logado.id)

            form.instance.usuario_criador = usuario_logado
            form.instance.funcionario = funcionario
            
            return super().form_valid(form)

        except Exception as erro:
            return HttpResponse('Usuário não possui vínculo com funcionário!') # !! VERIFICAR A MELHOR FORMA DE INFORMAR A EXCEÇÃO PARA O USUÁRIO !!

    def get_form(self, form_class=None):
        """
            - Função Bilt-in do Django que possibilita ajustar o queryset do atributo antes de exibir o formulário. 
        """
        form = super().get_form(form_class)
        form.fields['municipio'].queryset = MunicipioAdm.objects.filter(ativo=True)

        return form

###### UPDATE ######
class AtendimentoUpdate(UpdateView):
    model = Atendimento
    fields = ['municipio', 'data_atendimento', 'cliente', 'descricao']

###### DELETE ######
class AtendimentoDelete(DeleteView):
    model = Atendimento
    template_name = 'atendimento/deletes/atendimento_delete.html'
    success_url = reverse_lazy('atendimento-list')
    
def filtrar_atendimentos(request):
    """
        Função criada para fazer a requisição http dos filtros utilizados na lista de atendimentos e retornar o Queryset de acordo com os filtros.
    """
    filtro_inicial = request.GET.get('data_inicial')
    filtro_final = request.GET.get('data_final')
    filtro_municipio = request.GET.get('municipio')
    filtro_funcionario = request.GET.get('funcionario') 


    filtro_inicial = filtro_inicial or None
    filtro_final = filtro_final or None

    # Através do id do funcionario obtido do http request eu pego com o método get a instância(objeto) do funcionário e através da instância eu acesso e salvo em uma variável o id do usuário vinculado à instância funcionário.
    if filtro_funcionario:
        funcionario = Funcionario.objects.get(id=filtro_funcionario)
        id_usuario_criador = funcionario.usuario.id
    else:
        id_usuario_criador = None
    
    if filtro_inicial and filtro_final and filtro_municipio and filtro_funcionario:
        atendimentos = Atendimento.objects.filter(data__range=(filtro_inicial, filtro_final), municipio=filtro_municipio, usuario_criador=id_usuario_criador, ativo=True)       

    elif filtro_inicial and filtro_final and filtro_municipio:
        atendimentos = Atendimento.objects.filter(data__range=(filtro_inicial, filtro_final), municipio=filtro_municipio, ativo=True)

    elif filtro_inicial and filtro_final and filtro_funcionario:
        atendimentos = Atendimento.objects.filter(data__range=(filtro_inicial, filtro_final), usuario_criador=id_usuario_criador, ativo=True)

    else:
        atendimentos = Atendimento.objects.filter(data__range=(filtro_inicial, filtro_final), ativo=True)
    
    return atendimentos.order_by('data')        
# ----------------------------------------------------------

###### LIST ######
class AtendimentoList(ListView):
    model = Atendimento
    template_name = 'atendimento/lists/atendimento_list.html'

    def get_context_data(self, **kwargs):
        """
            - Esta função é uma função bilt-in do Django que possibilita criar um iterador personalizado.
        """
        context = super().get_context_data(**kwargs)
        context['municipios'] = MunicipioAdm.objects.filter(ativo=True)
        context['funcionarios'] = Funcionario.objects.filter(ativo=True)

        return context

    def get_queryset(self):
        return filtrar_atendimentos(self.request)
        
# class Pdf(View):
#     model = Atendimento

    
