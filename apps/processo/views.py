from .models import MunicipioAdm, ProcessoAdm, AndamentoAdm, Auditoria, TipoAndamentoAdm, Assunto
from django.views.generic.edit import CreateView, UpdateView, DeleteView # Módulo para create, update e delete
from django.views.generic.list import ListView # Módulo para list
from django.views.generic import TemplateView, View
from django.urls import reverse, reverse_lazy # Módulo para reverter para a url definida após ter sucesso na execução
from datetime import datetime # Módulo para datas
from django.contrib.auth.models import User
import os # Módulo para trabalhar com pastas e arquivos
from docx2pdf import convert # Módulo para converter .docx em pdf
from PyPDF2 import PdfMerger # Módulo para mesclar pdf
from django.core.exceptions import ValidationError
from django.http import HttpResponse
import logging # Módulo para registro de logs
logger = logging.getLogger('auditoria_erros') # 'logger' recebe o logger configurado no settings.

from PIL import Image # Da biblioteca Pillow, para lidar com imagens.

from urllib.parse import urlencode # O 'urlencode()' converte os parâmetros de consulta em uma string de consulta válida, pega um dicionario e converte para Ex. filtro1=valor1&filtro2=valor2. 

# Relatórios
from fpdf import FPDF
import tempfile
import os
 
###### VIEW ######
class ProcessoAdmView(TemplateView):
    template_name = 'processos/views/processo_adm_view.html'

    # Função para iterar com os dados do processo
    def get_context_data(self, **kwargs):
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL  

        context = super().get_context_data(**kwargs)
        context['url_retorno'] = reverse('proc-adm-list') + '?' + self.request.GET.urlencode()
        context['dados_processo'] = ProcessoAdm.objects.filter(pk=processo_pk) # Filtra os dados do processo através da pk
        return context

class ProcessoAdmArquivadoView(TemplateView):
    template_name = 'processos/views/processo_adm_arquivado_view.html'

    # Função para iterar com os dados do processo
    def get_context_data(self, **kwargs):
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL  

        context = super().get_context_data(**kwargs)
        context['dados_processo'] = ProcessoAdm.objects.filter(pk=processo_pk) # Filtra os dados do processo através da pk
        return context
    
class AndamentoAdmView(TemplateView):
    template_name ='processos/views/andamento_adm_view.html'

     #  Função para reverter para a url 'andamento-adm-list' passando a pk do processo para conseguir voltar para a tela de lista de andamentos do processo.
    def get_voltar(self, processo_pk):
        return reverse('andamento-adm-list-update', args=[processo_pk])

    # Função para funcionalidade do botão 'voltar'
    # Função para buscar a pk do processo e salvar na variável 'processo_pk', com a funcionalidade do get_context_data envia para o Template o contexto 'cancelar' que recebe a função 'get_cancelar' junto com a variavel 'processo_pk'.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        andamento_pk = self.kwargs.get('pk') # Pega a PK do andamento ao fazer o update através da URL
        andamento = AndamentoAdm.objects.get(pk=andamento_pk) # Busca o andamento através da PK do andamento
        processo_pk = andamento.processo_id # Busca a PK do processo através do andamento (processo_id é a ForeignKey entre o processo administrativo e o andamento)

        context['voltar'] = self.get_voltar(processo_pk)
        context['dados_andamento'] = AndamentoAdm.objects.filter(pk=andamento_pk) # Filtra os dados do andamento através da pk, para conseguir iterar com os dados do andamento

        return context

class GerarRelatorio(TemplateView):
    model = ProcessoAdm
    template_name = 'processos/views/gera_relatorio_view.html'

    def get_context_data(self, **kwargs):
        municipios = MunicipioAdm.objects.filter(tipo_contrato='Assessoria', ativo=True).order_by('nome')

        context = super().get_context_data(**kwargs)
        context['municipios'] = municipios

        return context
    
class MesclarPDFsView(View):
    """
        Realiza a mesclagem dos arquivos pdf com o campo checkbox selecionado, disponibilizando o download do arquivo mesclado direto no navegador, sem alterar os arquivos originais.

        Através de um formulário post enviado por um botão submit, pega os pdfs com o checkbox selecionado através do name do checkbox.

        Através do id passado no value do checkbox, pega o atributo arquivo e realiza um append para o PdfMerger, realiza a mesclagem e disponibiliza o arquivo através do HttpResponse.

    """
    def post(self, request):
        try:
            pdf_selecionados = request.POST.getlist('pdf_selecionados')

            # Crie um objeto PdfMerger para mesclar os arquivos PDF
            merger = PdfMerger()

            for pdf_id in pdf_selecionados:
                registro = AndamentoAdm.objects.get(id=pdf_id)
                merger.append(registro.arquivo.path)

            # Crie uma resposta para download do PDF mesclado
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="pdf_mesclado.pdf"'

            # Mescle os PDFs e envie a resposta
            merger.write(response)
            merger.close()

            return response
        
        except Exception as erro:
            logger.error(f'Erro ao mesclar PDF - View: MesclarPDFsView - Erro: {str(erro)}')

class ProcessoAdmCreate(CreateView):
    model = ProcessoAdm
    template_name = 'processos/creates/processo_adm_create.html'
    fields = ['numero', 'municipio', 'uf', 'data_inicial', 'data_final', 'data_div_ativa', 'valor_atributo', 'valor_multa', 'valor_credito', 'valor_atualizado', 'data_valor_atualizado', 'nome_contribuinte', 'tipo_pessoa', 'documento', 'nome_fantasia', 'email', 'endereco', 'complemento', 'municipio_contribuinte', 'uf_contribuinte', 'cep', 'telefone', 'celular']
    success_url = reverse_lazy('proc-adm-list')

    def form_valid(self, form):
        form.instance.usuario_criador = self.request.user 

        numero_processo = form.cleaned_data['numero'] # Pega o valor do atributo 'numero' preenchido no formulário...
        municipio = form.cleaned_data['municipio']

        # # CONDIÇÃO PARA BLOQUEAR O USUÁRIO DE CRIAR MAIS DE UM PROCESSO COM O MESMO NÚMERO PARA O MESMO MUNICÍPIO.
        if ProcessoAdm.objects.filter(numero=numero_processo, municipio=municipio).exists(): # Se o objeto filtrado existir, o exists(), retorna True.
            form.add_error(None, "Já existe um processo com esse código vinculado a este município!") # Inserindo o erro no formulário.
            return self.form_invalid(form)  # Retorna um formulário inválido para exibir os erros
        
        try:    
            result = super().form_valid(form) # Salvando o formulário na variável

            # Registre a operação de criação na auditoria do banco de dados
            Auditoria.objects.create(
                usuario = self.request.user,
                objeto_id = self.object.id,
                tipo_objeto = 'processo administrativo',
                view = ProcessoAdmCreate,
                acao = 'create',
                processo = self.object.numero,
                )
            
            return result # Retorna a variável contendo o formulário válido.
        
        except Exception as erro:
            logger.error(f'Erro ao criar objeto - View: ProcessoAdmCreate - Erro: {str(erro)}')
            return super().form_invalid(form) # Se a condição com exists() retornar False, retorna o formulário inválido.

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['municipio'].queryset = MunicipioAdm.objects.filter(tipo_contrato='Assessoria', ativo=True).order_by('nome')

        return form

class AndamentoAdmCreate(CreateView):  
    model = AndamentoAdm
    template_name = 'processos/creates/andamento_adm_create.html'
    fields = ['data_andamento', 'tipo_andamento', 'funcionario', 'localizacao_processo', 'situacao_pagamento', 'valor_pago', 'data_prazo', 'data_recebimento', 'assunto', 'arquivo']
    success_url = reverse_lazy('proc-adm-list')

    def form_valid(self, form):
        """
            A função form_valid() serve para alterar os valores do atributo ou realizar qualquer ação antes que o formulário seja salvo.
        """
        try:
            pk_processo = self.kwargs.get('pk')
            form.instance.processo_id = pk_processo

            # Preencher o atributo 'criador_andamento_adm' com o ID do usuário logado.
            form.instance.usuario_criador = self.request.user 

            result = super().form_valid(form)
            
            # Registre a operação de criação na auditoria
            Auditoria.objects.create(
                usuario = self.request.user,
                objeto_id = self.object.id,
                tipo_objeto = 'andamento administrativo',
                view = AndamentoAdmCreate,
                acao = 'create',
                andamento = self.object.tipo_andamento,
                processo = self.object.processo,
                )

            return result
        
        except Exception as erro:
            logger.error(f'Erro ao criar objeto - View: AndamentoAdmCreate - Erro: {str(erro)}')
    
    # Após realizar o create do andamento com sucesso, reverte para a lista de andamentos do processo 
    def get_success_url(self):
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL       

        return reverse('andamento-adm-list-update', args=[processo_pk])
    
    # Função para reverter para a url 'andamento-adm-list' passando a pk do processo para conseguir voltar para a tela de lista de andamentos do processo.
    def get_cancelar(self, processo_pk):
        return reverse('andamento-adm-list-update', args=[processo_pk])
    
    # Função para iterar com os dados do processo na view de create andamento
    def get_context_data(self, **kwargs):
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL  

        context = super().get_context_data(**kwargs)
        context['dados_processo'] = ProcessoAdm.objects.filter(pk=processo_pk) # Filtra os dados do processo através da pk

        context['funcionarios'] = User.objects.filter(is_staff=True)  # Criei um iterador 'funcionarios' para preencher o select do campo funcionario, apenas com usuarios Staff(membro da equipe).
        context['cancelar'] = self.get_cancelar(processo_pk)

        return context
    
    # O método get_form é usado para ajustar o queryset do campo tipo_andamento antes de exibir o formulário. Ele define o queryset para exibir apenas registros de TipoAndamento onde ativo=True.
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['tipo_andamento'].queryset = TipoAndamentoAdm.objects.filter(ativo=True).order_by('tipo_andamento')
        form.fields['assunto'].queryset = Assunto.objects.filter(ativo=True).order_by('assunto')

        return form
    
###### UPDATE ######
class ProcessoAdmUpdate(UpdateView):
    model = ProcessoAdm
    template_name = 'processos/updates/processo_adm_update.html'
    fields = ['ativo', 'municipio', 'uf', 'data_inicial', 'data_final', 'data_div_ativa', 'valor_atributo', 'valor_multa', 'valor_credito', 'valor_atualizado', 'data_valor_atualizado', 'nome_contribuinte', 'tipo_pessoa', 'documento', 'nome_fantasia', 'email', 'endereco', 'complemento', 'municipio_contribuinte', 'uf_contribuinte', 'cep', 'telefone', 'celular']
    # success_url = reverse_lazy('proc-adm-list') - Foi subscrito pelo método get_sucess_url()

    # Função para iterar com os dados do processo na view de update processo
    def get_context_data(self, **kwargs):
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL  

        context = super().get_context_data(**kwargs)
        context['url_retorno'] = reverse('proc-adm-list') + '?' + self.request.GET.urlencode()
        context['dados_processo'] = ProcessoAdm.objects.filter(pk=processo_pk) # Filtra os dados do processo através da pk
        return context
    
    def get_success_url(self):
        url_retorno = reverse('proc-adm-list') + '?' + self.request.GET.urlencode()
        return url_retorno

    def form_valid(self, form):  
        """
            O código a seguir, verifica se algum dos campos do ProcessoAdm foi alterado durante o update, se ocorreu a alteração, será criado um objeto no modelo Auditoria com os dados de registro e os campos alterados
        """    
        try:
            objeto_original = self.get_object()
            objeto_atualizado = form.instance

            campos_alterados = []

            if objeto_original.ativo != objeto_atualizado.ativo:
                campos_alterados.append(f'| Campo: ativo ; Valor Antigo: {objeto_original.ativo} ; Valor Novo: {objeto_atualizado.ativo} |')
            
            if objeto_original.municipio != objeto_atualizado.municipio:
                campos_alterados.append(f'| Campo: municipio ; Valor Antigo: {objeto_original.municipio} ; Valor Novo: {objeto_atualizado.municipio} |')

            if objeto_original.uf != objeto_atualizado.uf:
                campos_alterados.append(f'| Campo: uf ; Valor Antigo: {objeto_original.uf} ; Valor Novo: {objeto_atualizado.uf} |')

            if objeto_original.data_inicial != objeto_atualizado.data_inicial:
                campos_alterados.append(f'| Campo: data_inicial ; Valor Antigo: {objeto_original.data_inicial} ; Valor Novo: {objeto_atualizado.data_inicial} |')

            if objeto_original.data_final != objeto_atualizado.data_final:
                campos_alterados.append(f'| Campo: data_final ; Valor Antigo: {objeto_original.data_final} ; Valor Novo: {objeto_atualizado.data_final} |')

            if objeto_original.data_div_ativa != objeto_atualizado.data_div_ativa:
                campos_alterados.append(f'| Campo: data_div_ativa ; Valor Antigo: {objeto_original.data_div_ativa} ; Valor Novo: {objeto_atualizado.data_div_ativa} |')

            if objeto_original.valor_atributo != objeto_atualizado.valor_atributo:
                campos_alterados.append(f'| Campo: valor_atributo ; Valor Antigo: {objeto_original.valor_atributo} ; Valor Novo: {objeto_atualizado.valor_atributo} |')

            if objeto_original.valor_multa != objeto_atualizado.valor_multa:
                campos_alterados.append(f'| Campo: valor_multa ; Valor Antigo: {objeto_original.valor_multa} ; Valor Novo: {objeto_atualizado.valor_multa} |')

            if objeto_original.valor_credito != objeto_atualizado.valor_credito:
                campos_alterados.append(f'| Campo: valor_credito ; Valor Antigo: {objeto_original.valor_credito} ; Valor Novo: {objeto_atualizado.valor_credito} |')

            if objeto_original.valor_atualizado != objeto_atualizado.valor_atualizado:
                campos_alterados.append(f'| Campo: valor_atualizado ; Valor Antigo: {objeto_original.valor_atualizado} ; Valor Novo: {objeto_atualizado.valor_atualizado} |')

            if objeto_original.data_valor_atualizado != objeto_atualizado.data_valor_atualizado:
                campos_alterados.append(f'| Campo: data_valor_atualizado ; Valor Antigo: {objeto_original.data_valor_atualizado} ; Valor Novo: {objeto_atualizado.data_valor_atualizado} |')

            if objeto_original.nome_contribuinte != objeto_atualizado.nome_contribuinte:
                campos_alterados.append(f'| Campo: nome_contribuinte ; Valor Antigo: {objeto_original.nome_contribuinte} ; Valor Novo: {objeto_atualizado.nome_contribuinte} |')

            if objeto_original.tipo_pessoa != objeto_atualizado.tipo_pessoa:
                campos_alterados.append(f'| Campo: tipo_pessoa ; Valor Antigo: {objeto_original.tipo_pessoa} ; Valor Novo: {objeto_atualizado.tipo_pessoa} |')

            if objeto_original.documento != objeto_atualizado.documento:
                campos_alterados.append(f'| Campo: documento ; Valor Antigo: {objeto_original.documento} ; Valor Novo: {objeto_atualizado.documento} |')

            if objeto_original.nome_fantasia != objeto_atualizado.nome_fantasia:
                campos_alterados.append(f'| Campo: nome_fantasia ; Valor Antigo: {objeto_original.nome_fantasia} ; Valor Novo: {objeto_atualizado.nome_fantasia} |')

            if objeto_original.email != objeto_atualizado.email:
                campos_alterados.append(f'| Campo: email ; Valor Antigo: {objeto_original.email} ; Valor Novo: {objeto_atualizado.email} |')

            if objeto_original.endereco != objeto_atualizado.endereco:
                campos_alterados.append(f'| Campo: endereco ; Valor Antigo: {objeto_original.endereco} ; Valor Novo: {objeto_atualizado.endereco} |')

            if objeto_original.complemento != objeto_atualizado.complemento:
                campos_alterados.append(f'| Campo: complemento ; Valor Antigo: {objeto_original.complemento} ; Valor Novo: {objeto_atualizado.complemento} |')

            if objeto_original.municipio_contribuinte != objeto_atualizado.municipio_contribuinte:
                campos_alterados.append(f'| Campo: municipio_contribuinte ; Valor Antigo: {objeto_original.municipio_contribuinte} ; Valor Novo: {objeto_atualizado.municipio_contribuinte} |')
                
            if objeto_original.uf_contribuinte != objeto_atualizado.uf_contribuinte:
                campos_alterados.append(f'| Campo: uf_contribuinte ; Valor Antigo: {objeto_original.uf_contribuinte} ; Valor Novo: {objeto_atualizado.uf_contribuinte} |')

            if objeto_original.cep != objeto_atualizado.cep:
                campos_alterados.append(f'| Campo: cep ; Valor Antigo: {objeto_original.cep} ; Valor Novo: {objeto_atualizado.cep} |')

            if objeto_original.telefone != objeto_atualizado.telefone:
                campos_alterados.append(f'| Campo: telefone ; Valor Antigo: {objeto_original.telefone} ; Valor Novo: {objeto_atualizado.telefone} |')

            if objeto_original.celular != objeto_atualizado.celular:
                campos_alterados.append(f'| Campo: celular ; Valor Antigo: {objeto_original.celular} ; Valor Novo: {objeto_atualizado.celular} |')

            if campos_alterados:
                # Registra a operação de alteração na auditoria
                Auditoria.objects.create(
                    usuario = self.request.user,
                    objeto_id = self.object.id,
                    tipo_objeto = 'processo administrativo',
                    view = ProcessoAdmUpdate,
                    acao = 'update',
                    processo = self.object.numero,
                    campos_alterados = campos_alterados,              
                )

            return super().form_valid(form)

        except Exception as erro:
            logger.error(f'Erro ao editar objeto - View: ProcessoAdmUpdate - Erro: {str(erro)}')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['municipio'].queryset = MunicipioAdm.objects.filter(tipo_contrato='Assessoria', ativo=True).order_by('nome')

        return form
           
class ProcessoAdmArquivadoUpdate(UpdateView):
    model = ProcessoAdm
    template_name = 'processos/updates/processo_adm_arquivado_update.html'
    fields = ['ativo', 'municipio', 'uf', 'data_inicial', 'data_final', 'data_div_ativa', 'valor_atributo', 'valor_multa', 'valor_credito', 'valor_atualizado', 'data_valor_atualizado', 'nome_contribuinte', 'tipo_pessoa', 'documento', 'nome_fantasia', 'email', 'endereco', 'complemento', 'municipio_contribuinte', 'uf_contribuinte', 'cep', 'telefone', 'celular']
    success_url = reverse_lazy('proc-adm-arquivado-list')

    # Função para iterar com os dados do processo na view de update processo
    def get_context_data(self, **kwargs):
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL  

        context = super().get_context_data(**kwargs)
        context['dados_processo'] = ProcessoAdm.objects.filter(pk=processo_pk) # Filtra os dados do processo através da pk
        return context
    
    def form_valid(self, form):  
        """
            O código a seguir, verifica se algum dos campos do ProcessoAdm foi alterado durante o update, se ocorreu a alteração, será criado um objeto no modelo Auditoria com os dados de registro e os campos alterados
        """    
        try:
            objeto_original = self.get_object()
            objeto_atualizado = form.instance

            campos_alterados = []

            if objeto_original.ativo != objeto_atualizado.ativo:
                campos_alterados.append(f'| Campo: ativo ; Valor Antigo: {objeto_original.ativo} ; Valor Novo: {objeto_atualizado.ativo} |')
            
            if objeto_original.municipio != objeto_atualizado.municipio:
                campos_alterados.append(f'| Campo: municipio ; Valor Antigo: {objeto_original.municipio} ; Valor Novo: {objeto_atualizado.municipio} |')

            if objeto_original.uf != objeto_atualizado.uf:
                campos_alterados.append(f'| Campo: uf ; Valor Antigo: {objeto_original.uf} ; Valor Novo: {objeto_atualizado.uf} |')

            if objeto_original.data_inicial != objeto_atualizado.data_inicial:
                campos_alterados.append(f'| Campo: data_inicial ; Valor Antigo: {objeto_original.data_inicial} ; Valor Novo: {objeto_atualizado.data_inicial} |')

            if objeto_original.data_final != objeto_atualizado.data_final:
                campos_alterados.append(f'| Campo: data_final ; Valor Antigo: {objeto_original.data_final} ; Valor Novo: {objeto_atualizado.data_final} |')

            if objeto_original.data_div_ativa != objeto_atualizado.data_div_ativa:
                campos_alterados.append(f'| Campo: data_div_ativa ; Valor Antigo: {objeto_original.data_div_ativa} ; Valor Novo: {objeto_atualizado.data_div_ativa} |')

            if objeto_original.valor_atributo != objeto_atualizado.valor_atributo:
                campos_alterados.append(f'| Campo: valor_atributo ; Valor Antigo: {objeto_original.valor_atributo} ; Valor Novo: {objeto_atualizado.valor_atributo} |')

            if objeto_original.valor_multa != objeto_atualizado.valor_multa:
                campos_alterados.append(f'| Campo: valor_multa ; Valor Antigo: {objeto_original.valor_multa} ; Valor Novo: {objeto_atualizado.valor_multa} |')

            if objeto_original.valor_credito != objeto_atualizado.valor_credito:
                campos_alterados.append(f'| Campo: valor_credito ; Valor Antigo: {objeto_original.valor_credito} ; Valor Novo: {objeto_atualizado.valor_credito} |')

            if objeto_original.valor_atualizado != objeto_atualizado.valor_atualizado:
                campos_alterados.append(f'| Campo: valor_atualizado ; Valor Antigo: {objeto_original.valor_atualizado} ; Valor Novo: {objeto_atualizado.valor_atualizado} |')

            if objeto_original.data_valor_atualizado != objeto_atualizado.data_valor_atualizado:
                campos_alterados.append(f'| Campo: data_valor_atualizado ; Valor Antigo: {objeto_original.data_valor_atualizado} ; Valor Novo: {objeto_atualizado.data_valor_atualizado} |')

            if objeto_original.nome_contribuinte != objeto_atualizado.nome_contribuinte:
                campos_alterados.append(f'| Campo: nome_contribuinte ; Valor Antigo: {objeto_original.nome_contribuinte} ; Valor Novo: {objeto_atualizado.nome_contribuinte} |')

            if objeto_original.tipo_pessoa != objeto_atualizado.tipo_pessoa:
                campos_alterados.append(f'| Campo: tipo_pessoa ; Valor Antigo: {objeto_original.tipo_pessoa} ; Valor Novo: {objeto_atualizado.tipo_pessoa} |')

            if objeto_original.documento != objeto_atualizado.documento:
                campos_alterados.append(f'| Campo: documento ; Valor Antigo: {objeto_original.documento} ; Valor Novo: {objeto_atualizado.documento} |')

            if objeto_original.nome_fantasia != objeto_atualizado.nome_fantasia:
                campos_alterados.append(f'| Campo: nome_fantasia ; Valor Antigo: {objeto_original.nome_fantasia} ; Valor Novo: {objeto_atualizado.nome_fantasia} |')

            if objeto_original.email != objeto_atualizado.email:
                campos_alterados.append(f'| Campo: email ; Valor Antigo: {objeto_original.email} ; Valor Novo: {objeto_atualizado.email} |')

            if objeto_original.endereco != objeto_atualizado.endereco:
                campos_alterados.append(f'| Campo: endereco ; Valor Antigo: {objeto_original.endereco} ; Valor Novo: {objeto_atualizado.endereco} |')

            if objeto_original.complemento != objeto_atualizado.complemento:
                campos_alterados.append(f'| Campo: complemento ; Valor Antigo: {objeto_original.complemento} ; Valor Novo: {objeto_atualizado.complemento} |')

            if objeto_original.municipio_contribuinte != objeto_atualizado.municipio_contribuinte:
                campos_alterados.append(f'| Campo: municipio_contribuinte ; Valor Antigo: {objeto_original.municipio_contribuinte} ; Valor Novo: {objeto_atualizado.municipio_contribuinte} |')
                
            if objeto_original.uf_contribuinte != objeto_atualizado.uf_contribuinte:
                campos_alterados.append(f'| Campo: uf_contribuinte ; Valor Antigo: {objeto_original.uf_contribuinte} ; Valor Novo: {objeto_atualizado.uf_contribuinte} |')

            if objeto_original.cep != objeto_atualizado.cep:
                campos_alterados.append(f'| Campo: cep ; Valor Antigo: {objeto_original.cep} ; Valor Novo: {objeto_atualizado.cep} |')

            if objeto_original.telefone != objeto_atualizado.telefone:
                campos_alterados.append(f'| Campo: telefone ; Valor Antigo: {objeto_original.telefone} ; Valor Novo: {objeto_atualizado.telefone} |')

            if objeto_original.celular != objeto_atualizado.celular:
                campos_alterados.append(f'| Campo: celular ; Valor Antigo: {objeto_original.celular} ; Valor Novo: {objeto_atualizado.celular} |')

            if campos_alterados:
                # Registra a operação de alteração na auditoria
                Auditoria.objects.create(
                    usuario = self.request.user,
                    objeto_id = self.object.id,
                    tipo_objeto = 'processo administrativo',
                    view = ProcessoAdmArquivadoUpdate,
                    acao = 'update',
                    processo = self.object.numero,
                    campos_alterados = campos_alterados,              
                )

            return super().form_valid(form)

        except Exception as erro:
            logger.error(f'Erro ao editar objeto - View: ProcessoAdmArquivadoUpdate - Erro: {str(erro)}')

class AndamentoAdmUpdate(UpdateView):
    model = AndamentoAdm
    template_name = 'processos/updates/andamento_adm_update.html'
    fields = ['data_andamento', 'tipo_andamento', 'situacao_pagamento','valor_pago', 'data_prazo', 'data_recebimento', 'assunto', 'arquivo']

    # Após realizar o update com sucesso, reverte para a lista de andamentos do processo
    def get_success_url(self):
        andamento_pk = self.kwargs.get('pk') # Pega a PK do andamento ao fazer o update, através da URL
        andamento = AndamentoAdm.objects.get(pk=andamento_pk) # Busca o andamento através da PK do andamento
        processo_pk = andamento.processo_id # Busca a PK do processo através do andamento (processo_id é a ForeignKey entre o processo administrativo e o andamento)

        return reverse('andamento-adm-list-update', args=[processo_pk]) # URL da lista de andamentos + pk do processo 
    
    #  Função para reverter para a url 'andamento-adm-list' passando a pk do processo para conseguir voltar para a tela de lista de andamentos do processo.
    def get_cancelar(self, processo_pk):
        return reverse('andamento-adm-list-update', args=[processo_pk])

    # Função para funcionalidade do botão 'Cancelar'
    # Função para buscar a pk do processo e salvar na variável 'processo_pk', com a funcionalidade do get_context_data envia para o Template o contexto 'cancelar' que recebe a função 'get_cancelar' junto com a variavel 'processo_pk'.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        andamento_pk = self.kwargs.get('pk') # Pega a PK do andamento ao fazer o update através da URL
        andamento = AndamentoAdm.objects.get(pk=andamento_pk) # Busca o andamento através da PK do andamento
        processo_pk = andamento.processo_id # Busca a PK do processo através do andamento (processo_id é a ForeignKey entre o processo administrativo e o andamento)

        context['cancelar'] = self.get_cancelar(processo_pk)
        context['dados_andamento'] = AndamentoAdm.objects.filter(pk=andamento_pk) # Filtra os dados do andamento através da pk, para conseguir iterar com os dados do andamento

        return context
    
    def form_valid(self, form):
        """
            A função form_valid() serve para alterar os valores do atributo ou realizar qualquer ação antes que o formulário seja salvo.
        """
        try:
            objeto_original = self.get_object()
            objeto_atualizado = form.instance

            campos_alterados = []

            if objeto_original.data_andamento != objeto_atualizado.data_andamento:
                campos_alterados.append(f'| Campo: data_andamento ; Valor Antigo: {objeto_original.data_andamento} ; Valor Novo: {objeto_atualizado.data_andamento} |')

            if objeto_original.tipo_andamento != objeto_atualizado.tipo_andamento:
                campos_alterados.append(f'| Campo: tipo_andamento ; Valor Antigo: {objeto_original.tipo_andamento} ; Valor Novo: {objeto_atualizado.tipo_andamento} |')

            if objeto_original.situacao_pagamento != objeto_atualizado.situacao_pagamento:
                campos_alterados.append(f'| Campo: situacao_pagamento ; Valor Antigo: {objeto_original.situacao_pagamento} ; Valor Novo: {objeto_atualizado.situacao_pagamento} |')

            if objeto_original.valor_pago != objeto_atualizado.valor_pago:
                campos_alterados.append(f'| Campo: valor_pago ; Valor Antigo: {objeto_original.valor_pago} ; Valor Novo: {objeto_atualizado.valor_pago} |')

            if objeto_original.data_prazo != objeto_atualizado.data_prazo:
                campos_alterados.append(f'| Campo: data_prazo ; Valor Antigo: {objeto_original.data_prazo} ; Valor Novo: {objeto_atualizado.data_prazo} |')

            if objeto_original.data_recebimento != objeto_atualizado.data_recebimento:
                campos_alterados.append(f'| Campo: data_recebimento ; Valor Antigo: {objeto_original.data_recebimento} ; Valor Novo: {objeto_atualizado.data_recebimento} |')
            
            if objeto_original.assunto != objeto_atualizado.assunto:
                campos_alterados.append(f'| Campo: assunto ; Valor Antigo: {objeto_original.assunto} ; Valor Novo: {objeto_atualizado.assunto} |')

            if objeto_original.arquivo != objeto_atualizado.arquivo:
                campos_alterados.append(f'| Campo: arquivo ; Valor Antigo: {objeto_original.arquivo} ; Valor Novo: {objeto_atualizado.arquivo} |')
            
            if campos_alterados:
                # Registra a operação de update na auditoria
                Auditoria.objects.create(
                    usuario = self.request.user,
                    objeto_id = self.object.id,
                    tipo_objeto = 'andamento administrativo',
                    view = AndamentoAdmUpdate,
                    acao = 'update',
                    andamento = self.object.tipo_andamento,
                    processo = self.object.processo,
                    campos_alterados = campos_alterados,
                    )
                                
            return super().form_valid(form)

        except Exception as erro:
            logger.error(f'Erro ao editar objeto - View: AndamentoAdmUpdate - Erro: {str(erro)}')

    # O método get_form é usado para ajustar o queryset do campo tipo_andamento antes de exibir o formulário. Ele define o queryset para exibir apenas registros de TipoAndamento onde ativo=True.
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['tipo_andamento'].queryset = TipoAndamentoAdm.objects.filter(ativo=True).order_by('tipo_andamento')

        return form

###### DELETE ######
class ProcessoAdmDelete(DeleteView):
    model = ProcessoAdm
    template_name = 'processos/deletes/processo_adm_delete.html'
    # success_url = reverse_lazy('proc-adm-list')

    def form_valid(self, form):        
        try:
            # Registre a operação de criação na auditoria
            Auditoria.objects.create(
                usuario = self.request.user,
                objeto_id = self.object.id,
                tipo_objeto = 'processo administrativo',
                view = ProcessoAdmDelete,
                acao = 'delete',
                processo = self.object.numero,
                )
            
            return super().form_valid(form)
        
        except Exception as erro:
            logger.error(f'Erro ao deletar objeto - View: ProcessoAdmDelete - Erro: {str(erro)}')
    
    # Função para iterar com os dados do processo na view de delete processo
    def get_context_data(self, **kwargs):
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL  
        context = super().get_context_data(**kwargs)
        context['url_retorno'] = reverse('proc-adm-list') + '?' + self.request.GET.urlencode()
        context['dados_processo'] = ProcessoAdm.objects.filter(pk=processo_pk) # Filtra os dados do processo através da pk

        return context 
    
    def get_success_url(self):
        url_retorno = reverse('proc-adm-list') + '?' + self.request.GET.urlencode()
        return url_retorno

class ProcessoAdmArquivadoDelete(DeleteView):
    model = ProcessoAdm
    template_name = 'processos/deletes/processo_adm_arquivado_delete.html'
    success_url = reverse_lazy('proc-adm-arquivado-list')

    def form_valid(self, form):        
        try:
            # Registre a operação de criação na auditoria
            Auditoria.objects.create(
                usuario = self.request.user,
                objeto_id = self.object.id,
                tipo_objeto = 'processo administrativo',
                view = ProcessoAdmArquivadoDelete,
                acao = 'delete',
                processo = self.object.numero,
                )
            
            return super().form_valid(form)
        
        except Exception as erro:
            logger.error(f'Erro ao deletar objeto - View: ProcessoAdmArquivadoDelete - Erro: {str(erro)}')
    
    # Função para iterar com os dados do processo na view de delete processo
    def get_context_data(self, **kwargs):
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL  

        context = super().get_context_data(**kwargs)
        context['dados_processo'] = ProcessoAdm.objects.filter(pk=processo_pk) # Filtra os dados do processo através da pk
        return context 

class AndamentoAdmDelete(DeleteView):
    model = AndamentoAdm
    template_name = 'processos/deletes/andamento_adm_delete.html'

    def form_valid(self, form):    
        try:
            # Registre a operação de criação na auditoria
            Auditoria.objects.create(
                usuario = self.request.user,
                objeto_id = self.object.id,
                tipo_objeto = 'andamento administrativo',
                view = AndamentoAdmDelete,
                acao = 'delete',
                andamento = self.object.tipo_andamento,
                processo = self.object.processo,
                )
            
            return super().form_valid(form)
        
        except Exception as erro:
            logger.error(f'Erro ao deletar objeto - View: AndamentoAdmDelete - Erro: {str(erro)}')

    # Após realizar o delete com sucesso, reverte para a lista de andamentos do processo
    def get_success_url(self):
        andamento_pk = self.kwargs.get('pk') # Pega a PK do andamento ao fazer o update através da URL
        andamento = AndamentoAdm.objects.get(pk=andamento_pk) # Busca o andamento através da PK do andamento
        processo_pk = andamento.processo_id # Busca a PK do processo através do andamento (processo_id é a ForeignKey entre o processo administrativo e o andamento)

        return reverse('andamento-adm-list-update', args=[processo_pk]) # URL da lista de andamentos + pk do processo
    
    # Função para iterar com os dados do andamento na view de delete andamento
    def get_context_data(self, **kwargs):
        andamento_pk = self.kwargs.get('pk') # Pega a PK do andamento através da URL  

        context = super().get_context_data(**kwargs)
        context['dados_andamento'] = AndamentoAdm.objects.filter(pk=andamento_pk) # Filtra os dados do andamento através da pk
        return context

def filtrar_processos(request):
    """
        Função criada para fazer a requisição http dos filtros utilizados na lista de processos e retornar o Queryset de acordo com os filtros.
    """
    filtro_numero_processo = request.GET.get('numero')
    filtro_municipio = request.GET.get('municipio')

    if filtro_numero_processo and filtro_municipio:
        processos = ProcessoAdm.objects.filter(numero__icontains=filtro_numero_processo, municipio=filtro_municipio, ativo=True)

    elif filtro_numero_processo:
        processos = ProcessoAdm.objects.filter(numero__icontains=filtro_numero_processo, ativo=True)
    
    elif filtro_municipio:
        processos = ProcessoAdm.objects.filter(municipio=filtro_municipio, ativo=True)

    else:
        processos = []
    
    return processos

from django.shortcuts import redirect
###### LIST ######
class ProcessoAdmList(ListView):
    model = ProcessoAdm
    template_name = 'processos/lists/processo_adm_list.html'

    # Listar Apenas Processos Ativos
    def get_queryset(self):         
        return filtrar_processos(self.request)
        
    def get_context_data(self, **kwargs):
        processos = ProcessoAdm.objects.all()

        """
            (Executados)
            -> Todos os processos que possuem como último andamento, o andamento "Execução".

            ID = 14 -> EXECUÇÃO

            -> Se após o andamento de execução for criado algum andamento da lista à baixo, o processo sairá do status de Executados e irá para o status do novo andamento.
             
            ID = 15 -> CONFISSÃO DE DÍVIDA (PARCELAMENTO)
            ID = 26 -> ENCERRADO
            ID = 28 -> PARCELAMENT- DE DÉBITOS
            ID = 31 -> ARQUIVADO
            ID = 58 -> TERMO DE QUEBRA DE PARCELAMENTO
            ID = 64 -> LEVANTAMENTO DE ALVARÁ JUDICIAL
            ID = 66 -> PAGAMENTO - DURANTE O PROCESSO


            -> Então se após o andamento de execução for criado um novo andamento e for diferente dos andamentos listados à cima, o processo permanece no status de executados.    
            
        """

        processos = ProcessoAdm.objects.all()
        
        processos_executados = []
        total_credito = []

        for processo in processos:
            armazena_create_id = []   # O id de criação do andamento na tabela do banco de dados
            armazena_tipo_andamento_id = [] # O id do tipo_andamento
            
            if processo.ativo == True:
                andamentos_do_processo = processo.andamentoadm_set.all()
                for andamento in andamentos_do_processo:
                    armazena_tipo_andamento_id.append(andamento.tipo_andamento_id)
                    armazena_create_id.append(andamento.id)

            if armazena_create_id:
                andamento_atual_id = max(armazena_create_id)
                andamento_atual = processo.andamentoadm_set.get(id=andamento_atual_id)
            
                if andamento_atual.tipo_andamento.id == 14: # Id do tipo andamento = Execução
                    processos_executados.append(processo)
                    total_credito.append(processo.valor_credito)
                
                else:
                    if 14 in armazena_tipo_andamento_id:
                        if andamento_atual.tipo_andamento.id != 66 and andamento_atual.tipo_andamento.id != 26 and andamento_atual.tipo_andamento.id != 15 and andamento_atual.tipo_andamento.id != 31 and andamento_atual.tipo_andamento.id != 58 and andamento_atual.tipo_andamento.id != 64 and andamento_atual.tipo_andamento.id != 28:
                            processos_executados.append(processo)
                            total_credito.append(processo.valor_credito)
            else:
                andamento_atual_id = 0

            armazena_create_id.clear() # Limpa a lista de id para o próximo processo.

    #    -----------------------------------------------------------------------------------------------------

        """
            (Arquivados)
            -> Processos com o atributo "Ativo" desmarcado.
            -> Utilizado para casos em que o lançamento não é mais necessário no sistema, mas não é interessante excluir pois pode acontecer de ser utilizado depois...
        """

        processos_arquivados = processos.filter(ativo=False)

    #    -----------------------------------------------------------------------------------------------------

        """
            (Recebidos) 
            -> Não importa qual o último andamento do processo, se existir na lista de andamentos do processo um andamento da lista à baixo e possua o atributo "situacao_pagamento" == "Com Pagamento", ele deve ter o status de Recebidos.

            Lista de andamentos que ao selecionado abri o campo para informar a situação do pagamento e pagamento:
            ID = 15 - CONFISSÃO DE DÍVIDA (PARCELAMENTO)
            ID = 26 - ENCERRADO
            ID = 28 - PARCELAMENTO DE DÉBITOS
            ID = 58 - TERMO DE QUEBRA DE PARCELAMENTO
            ID = 64 - LEVANTAMENTO DE ALVARÁ JUDICIAL
            ID = 66 - PAGAMENTO - DURANTE O PROCESSO
           
        """
        processos_recebidos = []
        total_pago = []

        for processo in processos:
            if processo.ativo == True:
                andamentos_do_processo = processo.andamentoadm_set.all()
                for andamento in andamentos_do_processo:
                    if andamento.tipo_andamento_id == 26 or andamento.tipo_andamento_id == 58 or andamento.tipo_andamento_id == 64 or andamento.tipo_andamento_id == 66 or andamento.tipo_andamento_id == 28 or andamento.tipo_andamento_id == 15:
                        if andamento.situacao_pagamento == 'Com Pagamento':
                            valor_pago = andamento.valor_pago
                            processos_recebidos.append((processo, valor_pago))
                            total_pago.append(andamento.valor_pago)
                    else:
                        total_pago.append(0)

    #    -----------------------------------------------------------------------------------------------------

        """
            (Encerrados)
            -> Todos os processos que possuem como último andamento, um dos andamentos da lista à baixo:
        
            ID = 31 -> ARQUIVADO
            ID = 43 -> PARALISADO
            ID = 45 -> SUSPENSO
            ID = 52 -> EM FASE JUDICIAL
            ID = 55 -> SUSPENSO PARA FISCALIZAÇÃO FUTURA
            ID = 57 -> FIM DO CONTRATO COM A ASSESSORIA
            ID = 65 -> EXIGIBILIDADE SUSPENSA POR AÇÃO JUDICIAL

            ou

            -> Possua como último andamento, um dos andamentos da lista à baixo, com o atributo "situacao_pagamento" == "Sem Pagamento":
            
            Lista de andamentos que ao selecionado abri o campo para informar a situação do pagamento e pagamento:
            ID = 15 - CONFISSÃO DE DÍVIDA (PARCELAMENTO)
            ID = 26 - ENCERRADO
            ID = 28 - PARCELAMENTO DE DÉBITOS
            ID = 58 - TERMO DE QUEBRA DE PARCELAMENTO
            ID = 64 - LEVANTAMENTO DE ALVARÁ JUDICIAL
            ID = 66 - PAGAMENTO - DURANTE O PROCESSO

        """
        processos = ProcessoAdm.objects.all()

        processos_encerrados = []

        for processo in processos:
                armazena_andamento_create_id = []   # O id de criação do andamento na tabela do banco de dados
                armazena_tipo_andamento_id = [] # O id do tipo_andamento
                
                if processo.ativo == True:
                    andamentos_do_processo = processo.andamentoadm_set.all()
                    for andamento in andamentos_do_processo:
                        armazena_tipo_andamento_id.append(andamento.tipo_andamento_id)
                        armazena_andamento_create_id.append(andamento.id)
                        
                if armazena_andamento_create_id:
                    andamento_atual_id = max(armazena_andamento_create_id)
                    andamento_atual = processo.andamentoadm_set.get(id=andamento_atual_id)

                    if andamento_atual.tipo_andamento.id == 31 or andamento_atual.tipo_andamento.id == 43 or andamento_atual.tipo_andamento.id == 45 or andamento_atual.tipo_andamento.id == 52 or andamento_atual.tipo_andamento.id == 55 or andamento_atual.tipo_andamento.id == 57 or andamento_atual.tipo_andamento.id == 65 or andamento.tipo_andamento_id == 26 or andamento.tipo_andamento_id == 58 or andamento.tipo_andamento_id == 64 or andamento.tipo_andamento_id == 66 or andamento.tipo_andamento_id == 28 or andamento.tipo_andamento_id == 15:   
                        if andamento_atual.situacao_pagamento != 'Com Pagamento':
                            processos_encerrados.append(processo)
    
     #    -----------------------------------------------------------------------------------------------------

        """
            (Em Andamento)
            -> Todos os processos em que o último andamento não faz parte dos outros status.
        """
        armazena_tipo_andamento_id = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 29, 30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 46, 47, 48, 49, 51, 53, 54, 56, 59, 60, 61, 62, 63, 67, 68, 69, 70, 71]

        processos_em_andamento = []
        total_credito_geral = []
        
        for processo in processos:
                armazena_andamentos_id = []
                if processo.ativo == True:
                    andamentos_do_processo = processo.andamentoadm_set.all()
                    for andamento in andamentos_do_processo:
                        armazena_andamentos_id.append(andamento.id)

                if armazena_andamentos_id:
                    andamento_atual_id = max(armazena_andamentos_id) # Utiliza o max para descobrir o maior id, que no caso é o último criado
                    andamento_atual = processo.andamentoadm_set.get(id=andamento_atual_id) # Busca o último andamento através do maior id

                    if andamento_atual.tipo_andamento.id in armazena_tipo_andamento_id:
                        total_credito_geral.append(processo.valor_credito)
                        data_andamento = str(andamento_atual.data_andamento)
                        ano, mes, dia = data_andamento.split("-") # Desempacotamento
                        data_andamento = f'{dia}/{mes}/{ano}'
     
                        tipo_andamento = [andamento_atual.tipo_andamento]
                        processos_em_andamento.append((processo, data_andamento, tipo_andamento))

                else:
                    armazena_andamentos_id.append(0) # Para não ocorrer erro de sequência vazia ao executar o max com a lista vazia.

                armazena_andamentos_id.clear() # Limpa a lista de id para o próximo processo.

        context = super().get_context_data(**kwargs)

        # Contextos para Status Geral
        context['arquivados'] = len(processos_arquivados)
        context['executados'] = len(processos_executados)
        context['recebidos'] = len(processos_recebidos) 
        context['encerrados'] = len(processos_encerrados)
        context['andamentos'] = len(processos_em_andamento)
        context['total_pago'] = sum(total_pago)
        context['total_credito'] = sum(total_credito)
        context['total_credito_geral'] = sum(total_credito_geral)

        # Contextos para Filtros
        context['municipios'] = MunicipioAdm.objects.filter(tipo_contrato='Assessoria', ativo=True).order_by('nome')

        return context
    
class ProcessoAdmArquivadoList(ListView):

    """
    (Arquivados)
    -> Processos com o atributo "Ativo" desmarcado.

    -> Utilizado para casos em que o lançamento não é mais necessário no sistema, mas não é interessante excluir pois pode acontecer de ser utilizado depois..
    """ 

    model = ProcessoAdm
    template_name = 'processos/lists/processo_adm_arquivado_list.html'

    # Listar Apenas Processos Inativos
    def get_queryset(self):
        return ProcessoAdm.objects.filter(ativo=False)

class AndamentoAdmList(ListView):
    model = ProcessoAdm
    template_name = 'processos/lists/andamento_adm_list.html'
    
    def get_queryset(self):
        pk_processo = self.kwargs.get('pk') # Pega a pk(primary key) da URL, pk do processo
        
        processo = ProcessoAdm.objects.get(pk=pk_processo)  # Pega o processo que possui a pk recebida (pk é a primary key do processo)
        andamentos = processo.andamentoadm_set.filter(ativo=True).order_by('data_andamento')  # Pega todos os atributos do andamento, somente de andamentos ativos

        return andamentos
    
    # Função para iterar com os dados do processo na lista de andamentos
    def get_context_data(self, **kwargs):
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL  

        context = super().get_context_data(**kwargs)
        context['dados_processo'] = ProcessoAdm.objects.filter(pk=processo_pk) # Filtra os dados do processo através da pk
        return context

class AndamentoAdmListUpdate(ListView):
    """
        ListView do template que lista os andamentos do processo para editar, deletar e ver os andamentos.
    """
    model = ProcessoAdm
    template_name = 'processos/lists/andamento_adm_list_update.html'
    
    def get_queryset(self):
        pk_processo = self.kwargs.get('pk') # Pega a pk(primary key) da URL, pk do processo
        
        processo = ProcessoAdm.objects.get(pk=pk_processo)  # Pega o processo que possui a pk recebida (pk é a primary key do processo)
        andamentos = processo.andamentoadm_set.filter(ativo=True).order_by('data_andamento')  # Pega todos os atributos do andamento, somente de andamentos ativos e ordena pela data do andamento.

        # Para colocar o índice na coluna 'ordem' da lista.
        for indice, andamento in enumerate(andamentos): 
            andamento.ordem = indice + 1

        return andamentos
    
    # Função para iterar com os dados do processo na lista de andamentos
    def get_context_data(self, **kwargs):
        armazena_andamentos_id = []
        
        processo_pk = self.kwargs.get('pk') # Pega a PK do processo através da URL  

        processo = ProcessoAdm.objects.get(pk=processo_pk)

        andamentos = processo.andamentoadm_set.all()

        encaminhados = []

        if andamentos:

            for andamento in andamentos:
                armazena_andamentos_id.append(andamento.id)
                
                if andamento.tipo_andamento.id == 41: # ID = 41 - ENCAMINHAMENTO ( TIPO DE ANDAMENTO )
                    encaminhados.append(andamento)
        
            if encaminhados:
                ultimo_encaminhado = encaminhados[-1]
                funcionario = ultimo_encaminhado.funcionario

            else:
                for andamento in andamentos:
                    funcionario = andamento.usuario_criador.get_full_name

            if armazena_andamentos_id:
                andamento_atual_id = max(armazena_andamentos_id) # Utiliza o max para descobrir o maior id, que no caso é o último criado
                andamento_atual_get = processo.andamentoadm_set.get(id=andamento_atual_id) # Busca o último andamento através do maior id
                andamento_atual = str(andamento_atual_get.tipo_andamento)
                
        else:
            andamento_atual = ''
            funcionario = ''

        context = super().get_context_data(**kwargs)

        context['url_retorno'] = reverse('proc-adm-list') + '?' + self.request.GET.urlencode() # O context url_retorno, envia como contexto uma url contendo os filtros obtidos com o request.GET, contidos na url 'andamento-adm-list-update' que contem os filtros da url obtidos no template. O 'urlencode()' converte os parâmetros de consulta em uma string de consulta válida, pega um dicionario e converte para Ex. filtro1=valor1&filtro2=valor2. 
        context['dados_processo'] = ProcessoAdm.objects.filter(pk=processo_pk) # Filtra os dados do processo através da pk
        context['andamento_atual'] = andamento_atual
        context['funcionario'] = funcionario
        context['processo_pk'] = processo_pk # Enviando como contexto o id(pk) do processo para utilizar na ulr de create do andamento no template de listar andamentos, para que seja possível criar um andamento de dentro da lista de andamentos.

        return context

class ProcessoAdmExecutadoList(ListView):
    model = ProcessoAdm
    template_name = 'processos/lists/processo_adm_executado_list.html'

    def get_context_data(self, **kwargs):

        """
            (Executados)
            -> Todos os processos que possuem como último andamento, o andamento "Execução".

            ID = 14 -> EXECUÇÃO

            -> Se após o andamento de execução for criado algum andamento da lista à baixo, o processo sairá do status de Executados e irá para o status do novo andamento.
             
            ID = 15 -> CONFISSÃO DE DÍVIDA (PARCELAMENTO)
            ID = 26 -> ENCERRADO
            ID = 28 -> PARCELAMENT- DE DÉBITOS
            ID = 31 -> ARQUIVADO
            ID = 58 -> TERMO DE QUEBRA DE PARCELAMENTO
            ID = 64 -> LEVANTAMENTO DE ALVARÁ JUDICIAL
            ID = 66 -> PAGAMENTO - DURANTE O PROCESSO


            -> Então se após o andamento de execução for criado um novo andamento e for diferente dos andamentos listados à cima, o processo permanece no status de executados.    
            
        """

        processos = ProcessoAdm.objects.all()

        processos_executados = []
        total_credito = []

        for processo in processos:
            armazena_create_id = []   # O id de criação do andamento na tabela do banco de dados
            armazena_tipo_andamento_id = [] # O id do tipo_andamento
            
            if processo.ativo == True:
                andamentos_do_processo = processo.andamentoadm_set.all()
                for andamento in andamentos_do_processo:
                    armazena_tipo_andamento_id.append(andamento.tipo_andamento_id)
                    armazena_create_id.append(andamento.id)

            if armazena_create_id:
                andamento_atual_id = max(armazena_create_id)
                andamento_atual = processo.andamentoadm_set.get(id=andamento_atual_id)
            
                if andamento_atual.tipo_andamento.id == 14: # Id do tipo andamento = Execução
                    processos_executados.append(processo)
                    total_credito.append(processo.valor_credito)
                
                else:
                    if 14 in armazena_tipo_andamento_id:
                        if andamento_atual.tipo_andamento.id != 66 and andamento_atual.tipo_andamento.id != 26 and andamento_atual.tipo_andamento.id != 15 and andamento_atual.tipo_andamento.id != 31 and andamento_atual.tipo_andamento.id != 58 and andamento_atual.tipo_andamento.id != 64 and andamento_atual.tipo_andamento.id != 28:
                            processos_executados.append(processo)
                            total_credito.append(processo.valor_credito)
            else:
                andamento_atual_id = 0

            armazena_create_id.clear() # Limpa a lista de id para o próximo processo.

        context = super().get_context_data(**kwargs)
        context['processo_execucao'] = processos_executados
        context['total_credito'] = sum(total_credito)

        return context

class ProcessoAdmRecebidoList(ListView):
    model = ProcessoAdm
    template_name = 'processos/lists/processo_adm_recebido_list.html'

    """
        (Recebidos) 
        -> Não importa qual o último andamento do processo, se existir na lista de andamentos do processo um andamento da lista à baixo e possua o atributo "situacao_pagamento" == "Com Pagamento", ele deve ter o status de Recebidos.

        Lista de andamentos que ao selecionado abri o campo para informar a situação do pagamento e pagamento:
        ID = 15 - CONFISSÃO DE DÍVIDA (PARCELAMENTO)
        ID = 26 - ENCERRADO
        ID = 28 - PARCELAMENTO DE DÉBITOS
        ID = 58 - TERMO DE QUEBRA DE PARCELAMENTO
        ID = 64 - LEVANTAMENTO DE ALVARÁ JUDICIAL
        ID = 66 - PAGAMENTO - DURANTE O PROCESSO
           
    """

    def get_context_data(self, **kwargs):
        processos = ProcessoAdm.objects.all()

        processos_recebidos = []
        total_pago = []

        for processo in processos:
            if processo.ativo == True:
                andamentos_do_processo = processo.andamentoadm_set.all()
                for andamento in andamentos_do_processo:
                    if andamento.tipo_andamento_id == 26 or andamento.tipo_andamento_id == 58 or andamento.tipo_andamento_id == 64 or andamento.tipo_andamento_id == 66 or andamento.tipo_andamento_id == 28 or andamento.tipo_andamento_id == 15:
                        if andamento.situacao_pagamento == 'Com Pagamento':
                            valor_pago = andamento.valor_pago
                            processos_recebidos.append((processo, valor_pago))
                            total_pago.append(andamento.valor_pago)
                    else:
                        total_pago.append(0)

        context = super().get_context_data(**kwargs)
        context['processos_recebidos'] = processos_recebidos
        context['total_pago'] = sum(total_pago)

        return context
    
class ProcessoAdmEncerradoList(ListView):
    model = ProcessoAdm
    template_name = 'processos/lists/processo_adm_encerrado_list.html'

    """
        (Encerrados)
        -> Todos os processos que possuem como último andamento, um dos andamentos da lista à baixo:
    
        ID = 31 -> ARQUIVADO
        ID = 43 -> PARALISADO
        ID = 45 -> SUSPENSO
        ID = 52 -> EM FASE JUDICIAL
        ID = 55 -> SUSPENSO PARA FISCALIZAÇÃO FUTURA
        ID = 57 -> FIM DO CONTRATO COM A ASSESSORIA
        ID = 65 -> EXIGIBILIDADE SUSPENSA POR AÇÃO JUDICIAL

        ou

        -> Possua como último andamento, um dos andamentos da lista à baixo, com o atributo "situacao_pagamento" == "Sem Pagamento":
        
        Lista de andamentos que ao selecionado abri o campo para informar a situação do pagamento e pagamento:
        ID = 15 - CONFISSÃO DE DÍVIDA (PARCELAMENTO)
        ID = 26 - ENCERRADO
        ID = 28 - PARCELAMENTO DE DÉBITOS
        ID = 58 - TERMO DE QUEBRA DE PARCELAMENTO
        ID = 64 - LEVANTAMENTO DE ALVARÁ JUDICIAL
        ID = 66 - PAGAMENTO - DURANTE O PROCESSO

    """
    
    def get_context_data(self, **kwargs):
        processos = ProcessoAdm.objects.all()

        processos_encerrados = []

        for processo in processos:
                armazena_andamento_create_id = []   # O id de criação do andamento na tabela do banco de dados
                armazena_tipo_andamento_id = [] # O id do tipo_andamento
                
                if processo.ativo == True:
                    andamentos_do_processo = processo.andamentoadm_set.all()
                    for andamento in andamentos_do_processo:
                        armazena_tipo_andamento_id.append(andamento.tipo_andamento_id)
                        armazena_andamento_create_id.append(andamento.id)

                if armazena_andamento_create_id:
                    andamento_atual_id = max(armazena_andamento_create_id)
                    andamento_atual = processo.andamentoadm_set.get(id=andamento_atual_id)

                    if andamento_atual.tipo_andamento.id == 31 or andamento_atual.tipo_andamento.id == 43 or andamento_atual.tipo_andamento.id == 45 or andamento_atual.tipo_andamento.id == 52 or andamento_atual.tipo_andamento.id == 55 or andamento_atual.tipo_andamento.id == 57 or andamento_atual.tipo_andamento.id == 65 or andamento.tipo_andamento_id == 26 or andamento.tipo_andamento_id == 58 or andamento.tipo_andamento_id == 64 or andamento.tipo_andamento_id == 66 or andamento.tipo_andamento_id == 28 or andamento.tipo_andamento_id == 15: 
                        if andamento_atual.situacao_pagamento != 'Com Pagamento':
                            processos_encerrados.append(processo)
 
        context = super().get_context_data(**kwargs)
        context['processos_encerrados'] = processos_encerrados

        return context

class ProcessoAdmAndamentoList(ListView): # Em andamento
    """
        Dash board mostrado no template 'lista de processos administrativos' com dado de quantidade e valor de crédito de processos com andamentos diferentes de 'Execução' e 'Recebidos(encerrado com pagamento)'
    """
    model = ProcessoAdm
    template_name = 'processos/lists/processo_adm_andamento_list.html'

    def get_context_data(self, **kwargs):
        processos = ProcessoAdm.objects.all()

        """
            (Em Andamento)
            -> Todos os processos em que o último andamento não faz parte dos outros status.
        """
        armazena_tipo_andamento_id = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 29, 30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 46, 47, 48, 49, 51, 53, 54, 56, 59, 60, 61, 62, 63, 67, 68, 69, 70, 71]

        processos_em_andamento = []
        total_credito_geral = []
        
        for processo in processos:
                armazena_andamentos_id = []
                if processo.ativo == True:
                    andamentos_do_processo = processo.andamentoadm_set.all()
                    for andamento in andamentos_do_processo:
                        armazena_andamentos_id.append(andamento.id)

                if armazena_andamentos_id:
                    andamento_atual_id = max(armazena_andamentos_id) # Utiliza o max para descobrir o maior id, que no caso é o último criado
                    andamento_atual = processo.andamentoadm_set.get(id=andamento_atual_id) # Busca o último andamento através do maior id

                    if andamento_atual.tipo_andamento.id in armazena_tipo_andamento_id:
                        total_credito_geral.append(processo.valor_credito)
                        data_andamento = str(andamento_atual.data_andamento)
                        ano, mes, dia = data_andamento.split("-") # Desempacotamento
                        data_andamento = f'{dia}/{mes}/{ano}'
     
                        tipo_andamento = [andamento_atual.tipo_andamento]
                        processos_em_andamento.append((processo, data_andamento, tipo_andamento))

                else:
                    armazena_andamentos_id.append(0) # Para não ocorrer erro de sequência vazia ao executar o max com a lista vazia.

                armazena_andamentos_id.clear() # Limpa a lista de id para o próximo processo.

        context = super().get_context_data(**kwargs)
        context['processos_em_andamento'] = processos_em_andamento
        context['total_credito_geral'] = sum(total_credito_geral)

        return context

def pega_usuario(request):
    usuario = request.user
    return usuario

# GERAÇÃO DE RELATÓRIOS PERSONALIZADOS EM PDF 
class Estrutura_Pdf(FPDF): # Herda de FPDF
    """
        Gerar o cabeçario e rodapé padrão para todas as páginas do relatório.
    """
    def __init__(self, usuario_gerou, data_gerou, nome_municipio, brasao_municipio):
        super().__init__() #Inicializar a classe pai (super())
        self.usuario_gerou = usuario_gerou
        self.data_gerou = data_gerou
        self.nome_municipio = nome_municipio
        self.brasao_municipio = brasao_municipio

    def header(self):
        # Logo Aeg:
        self.image("apps/processo/static/img/aeg.png", 10, 8, 33)  # Eixo x:10 (horizontal), y: 8 (vertical), tamanho: 3
        self.ln(20) # Quebras de linha

        #  Logo Município:
        self.image(self.brasao_municipio, 165, 8, 25)  # Eixo x:10 (horizontal), y: 8 (vertical), tamanho: 3

        self.set_font('Arial', 'B', size=15)
        self.cell(187, -15, txt='Assessoria e Consultoria Tributária', ln=True, align='C')

        self.set_font('Arial', 'B', size=13)
        self.cell(188, 28, txt=f'Controle de Processos - {self.nome_municipio}', ln=True, align='C') # Eixo x:200

    def footer(self):
        # Position cursor at 1.5 cm from bottom:
        self.set_y(-15)
        # Settings rodapé
        self.set_font("helvetica", "I", 8)
        # Número de páginas no rodapé
        self.cell(0, 10, f'Página {self.page_no()}', align="C")
        self.cell(-350, 10, f'Usuário: {self.usuario_gerou}', 0, 0, 'C')
        self.cell(0, 10, f'{self.data_gerou}', 0, 0, 'R')
        
class Relatorio(View):
    """
        Gerar o relátorio geral
    """
    model = ProcessoAdm

    def get(self, request, *args, **kwargs):
        usuario_gerou = self.request.user.get_full_name()
        
        data_gerou = str(datetime.now())
        hora = data_gerou[-15:-7]
        data_gerou = data_gerou[:-16].split('-')
        data_gerou = f'Data: {data_gerou[2]}/{data_gerou[1]}/{data_gerou[0]} - {hora}h'

        # Busca valor Filtro - Faz a requisição do valor enviado pelo formulário para a url
        filtro_municipio = request.GET.get('municipio') # Filtar o atributo
        
        if filtro_municipio != "":

            get_municipio = MunicipioAdm.objects.get(id=filtro_municipio)
            nome_municipio = get_municipio.nome

            brasao_municipio = get_municipio.brasao.url # Com .url eu pego o path(caminho) da imagem salvo no banco de dados.
            brasao_municipio = brasao_municipio[1:]

            # Criar uma instância do PDF
            pdf = Estrutura_Pdf(usuario_gerou, data_gerou, nome_municipio, brasao_municipio) # Instanciando a função Pdf(FPDF) e passando variáveis como parâmetro para a função
            pdf.add_page()  
        
            # -------------------------------------------------------------------------------
            #  PROCESSOS - STATUS EM EXECUÇÃO

            pdf.set_font('Arial', 'B', size=13)
            pdf.cell(200, 10, 'Processos em Execução', align='C')
            pdf.ln(10)

            # Settings Tabelas (Configuração serve para todas as tabelas do relatório)
            pdf.set_font('Arial', 'B', size=10) # Letra
            pdf.set_draw_color(0, 152, 215) # Definir a cor da linha no formato RGB
            pdf.set_line_width(0.3) # Definir largura da linha   

            # Cabeçalho da tabela
            pdf.set_fill_color(0, 152, 215) # Definir a cor do cabeçalho da tabela, em RGB
            pdf.cell(115, 5, 'Empresa', 1, align='C', fill=True) # Eixo x:80 (horizontal), y:5 (vertical), o 1 inseri a tabela na linha.
            pdf.cell(22, 5, 'Processo', 1, align='C', fill=True) # fill=True - ativa o set_fill_color
            pdf.cell(31, 5, 'Crédito', 1, align='C', fill=True)
            pdf.cell(20, 5, 'Data', 1, align='C', fill=True)
            pdf.ln()



            # Construindo a queryset - filtro municipio irá receber a variável que contem o request do filtro de busca
            total_registros_execucao = 0
            total_credito = []

            processos_filtrados = ProcessoAdm.objects.filter(municipio=filtro_municipio)
            for processo in processos_filtrados:
                armazena_create_id = []   # O id de criação do andamento na tabela do banco de dados
                armazena_tipo_andamento_id = [] # O id do tipo_andamento
                
                if processo.ativo == True:
                    andamentos_do_processo = processo.andamentoadm_set.all()
                    for andamento in andamentos_do_processo:
                        armazena_tipo_andamento_id.append(andamento.tipo_andamento_id)
                        armazena_create_id.append(andamento.id)

                if armazena_create_id:
                    andamento_atual_id = max(armazena_create_id)
                    andamento_atual = processo.andamentoadm_set.get(id=andamento_atual_id)
                
                    if andamento_atual.tipo_andamento.id == 14: # Id do tipo andamento = Execução
                        total_registros_execucao += 1
                        total_credito.append(processo.valor_credito)

                        data_andamento = str(andamento_atual.data_andamento).split('-')
                        ano, mes, dia = data_andamento # Desempacotamento
                        data_andamento_convertida = f'{dia}/{mes}/{ano}'
                            
                        # Dados da tabela
                        pdf.set_font('Arial', size=9)
                        pdf.cell(115, 4, str(processo.nome_contribuinte[:82]), 1, align='L') # Eixo x:80 (largura horizontal do retangulo da coluna), y:10 (altura vertical do retangulo da coluna)
                        pdf.cell(22, 4, str(processo.numero), 1, align='C')
                        pdf.cell(31, 4, str(f'R$ {processo.valor_credito}'), 1, align='C')
                        pdf.cell(20, 4, str(data_andamento_convertida), 1, align='C')
                        pdf.ln()

            total_credito_execucao = sum(total_credito)

            # Totais
            pdf.set_font('Arial', size=9)
            pdf.cell(145, 10, txt=f'{total_registros_execucao} Registro(s)') #129: (posição horizontal do texto)
            pdf.cell(200, 10, txt=f'Total R$ {total_credito_execucao}', ln=True) # ln=True: Quebrar linha
            pdf.ln(5) # Pular 5 linhas

            # -------------------------------------------------------------------------------
            #  PROCESSOS - STATUS RECEBIDOS
                
            pdf.set_font('Arial', 'B', size=13)
            pdf.cell(200, 10, 'Processos Recebidos', align='C')
            pdf.ln(10)

            # Settings Tabelas (Configuração serve para todas as tabelas do relatório)
            pdf.set_font('Arial', 'B', size=10) # Letra
            pdf.set_draw_color(0, 152, 215) # Definir a cor da linha no formato RGB
            pdf.set_line_width(0.3) # Definir largura da linha   

            # Cabeçalho da tabela
            pdf.set_fill_color(0, 152, 215) # Definir a cor do cabeçalho da tabela
            pdf.cell(115, 5, 'Empresa', 1, align='C', fill=True)
            pdf.cell(22, 5, 'Processo', 1, align='C', fill=True)
            pdf.cell(31, 5, 'Pago', 1, align='C', fill=True)
            pdf.cell(20, 5, 'Data', 1, align='C', fill=True)
            pdf.ln()

            # Construindo a queryset
            total_registros_recebidos = 0
            total_pago = []

            processos_filtrados = ProcessoAdm.objects.filter(municipio=filtro_municipio)
            for processo in processos_filtrados:
                if processo.ativo == True:
                    andamentos_do_processo = processo.andamentoadm_set.all()
                    for andamento in andamentos_do_processo:
                        if andamento.tipo_andamento_id == 26 or andamento.tipo_andamento_id == 58 or andamento.tipo_andamento_id == 64 or andamento.tipo_andamento_id == 66 or andamento.tipo_andamento_id == 28 or andamento.tipo_andamento_id == 15:
                            if andamento.situacao_pagamento == 'Com Pagamento':
                                total_registros_recebidos += 1
                                total_pago.append(andamento.valor_pago)

                                data_andamento = str(andamento.data_andamento).split('-')
                                ano, mes, dia = data_andamento # Desempacotamento
                                data_andamento_convertida = f'{dia}/{mes}/{ano}'

                                # Dados da tabela
                                pdf.set_font('Arial', size=9)
                                pdf.cell(115, 4, str(processo.nome_contribuinte[:82]), 1, align='L')
                                pdf.cell(22, 4, str(processo.numero), 1, align='C')
                                pdf.cell(31, 4, str(f'R$ {andamento.valor_pago}'), 1, align='C')
                                pdf.cell(20, 4, str(data_andamento_convertida), 1, align='C')
                                pdf.ln()
                        else:
                            total_pago.append(0)

            total_valor_recebido = sum(total_pago)

            # Totais
            pdf.set_font('Arial', size=9)
            pdf.cell(145, 10, txt=f'{total_registros_recebidos} Registro(s)')
            pdf.cell(200, 10, txt=f'Total R$ {total_valor_recebido}', ln=True)
            pdf.ln(5) # Pular 5 linhas

            # -------------------------------------------------------------------------------
            #  PROCESSOS - STATUS ENCERRADOS

            pdf.set_font('Arial', 'B', size=13)
            pdf.cell(200, 10, 'Processos Encerrados', align='C')
            pdf.ln(10)

            # Settings Tabelas
            pdf.set_font('Arial', 'B', size=10) # Letra
            pdf.set_draw_color(0, 152, 215) # Definir a cor da linha no formato RGB
            pdf.set_line_width(0.3) # Definir largura da linha   

            # Cabeçalho da tabela
            pdf.set_fill_color(0, 152, 215) # Definir a cor do cabeçalho da tabela
            pdf.cell(115, 5, 'Empresa', 1, align='C', fill=True)
            pdf.cell(22, 5, 'Processo', 1, align='C', fill=True)
            pdf.cell(31, 5, 'Pago', 1, align='C', fill=True)
            pdf.cell(20, 5, 'Data', 1, align='C', fill=True)
            pdf.ln()

            # Construindo a queryset
            total_registros_encerrados = 0

            processos_filtrados = ProcessoAdm.objects.filter(municipio=filtro_municipio)
            for processo in processos_filtrados:
                    armazena_andamento_create_id = []   # O id de criação do andamento na tabela do banco de dados
                    armazena_tipo_andamento_id = [] # O id do tipo_andamento
                    
                    if processo.ativo == True:
                        andamentos_do_processo = processo.andamentoadm_set.all()
                        for andamento in andamentos_do_processo:
                            armazena_tipo_andamento_id.append(andamento.tipo_andamento_id)
                            armazena_andamento_create_id.append(andamento.id)

                    if armazena_andamento_create_id:
                        andamento_atual_id = max(armazena_andamento_create_id)
                        andamento_atual = processo.andamentoadm_set.get(id=andamento_atual_id)

                        if andamento_atual.tipo_andamento.id == 31 or andamento_atual.tipo_andamento.id == 43 or andamento_atual.tipo_andamento.id == 45 or andamento_atual.tipo_andamento.id == 52 or andamento_atual.tipo_andamento.id == 55 or andamento_atual.tipo_andamento.id == 57 or andamento_atual.tipo_andamento.id == 65 or andamento.tipo_andamento_id == 26 or andamento.tipo_andamento_id == 58 or andamento.tipo_andamento_id == 64 or andamento.tipo_andamento_id == 66 or andamento.tipo_andamento_id == 28 or andamento.tipo_andamento_id == 15: 
                            if andamento_atual.situacao_pagamento != 'Com Pagamento':
                                total_registros_encerrados += 1

                                data_andamento = str(andamento_atual.data_andamento).split('-')
                                ano, mes, dia = data_andamento # Desempacotamento
                                data_andamento_convertida = f'{dia}/{mes}/{ano}'

                                # Dados da tabela
                                pdf.set_font('Arial', size=9)
                                pdf.cell(115, 4, str(processo.nome_contribuinte[:82]), 1, align='L')
                                pdf.cell(22, 4, str(processo.numero), 1, align='C')
                                pdf.cell(31, 4, str('R$ 0.00'), 1, align='C')
                                pdf.cell(20, 4, str(data_andamento_convertida), 1, align='C')
                                pdf.ln()

            # Totais
            pdf.set_font('Arial', size=9)
            pdf.cell(145, 10, txt=f'{total_registros_encerrados} Registro(s)', ln=True)
            pdf.ln(5) # Pular 5 linhas

            # -------------------------------------------------------------------------------
            #  PROCESSOS - STATUS EM ANDAMENTO

            pdf.set_font('Arial', 'B', size=13)
            pdf.cell(200, 10, 'Processos Em Andamento', align='C')
            pdf.ln(10)

            # Settings Tabelas
            pdf.set_font('Arial', 'B', size=10) # Letra
            pdf.set_draw_color(0, 152, 215) # Definir a cor da linha no formato RGB
            pdf.set_line_width(0.3) # Definir largura da linha   

            # Cabeçalho da tabela
            pdf.set_fill_color(0, 152, 215) # Definir a cor do cabeçalho da tabela
            pdf.cell(70, 5, 'Empresa', 1, align='C', fill=True)
            pdf.cell(22, 5, 'Processo', 1, align='C', fill=True)
            pdf.cell(20, 5, 'Data', 1, align='C', fill=True)
            # pdf.cell(20, 5, 'Crédito', 1, align='C', fill=True)
            pdf.cell(76, 5, 'Tipo Andamento', 1, align='C', fill=True)
            pdf.ln()

            armazena_tipo_andamento_id = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 29, 30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 46, 47, 48, 49, 51, 53, 54, 56, 59, 60, 61, 62, 63, 67, 68, 69, 70, 71]

            total_registros_em_andamento = 0
            # total_credito_geral = []

            processos_filtrados = ProcessoAdm.objects.filter(municipio=filtro_municipio)
            for processo in processos_filtrados:
                    armazena_andamentos_id = []
                    if processo.ativo == True:
                        andamentos_do_processo = processo.andamentoadm_set.all()
                        for andamento in andamentos_do_processo:
                            armazena_andamentos_id.append(andamento.id)

                    if armazena_andamentos_id:
                        andamento_atual_id = max(armazena_andamentos_id) # Utiliza o max para descobrir o maior id, que no caso é o último criado
                        andamento_atual = processo.andamentoadm_set.get(id=andamento_atual_id) # Busca o último andamento através do maior id

                        if andamento_atual.tipo_andamento.id in armazena_tipo_andamento_id:
                            # total_credito_geral.append(processo.valor_credito)

                            data_andamento = str(andamento_atual.data_andamento).split("-")
                            ano, mes, dia = data_andamento # Desempacotamento
                            data_andamento_convertida = f'{dia}/{mes}/{ano}'
        
                            tipo_andamento = str(andamento_atual.tipo_andamento)
                            total_registros_em_andamento += 1

                            # Dados da tabela
                            pdf.set_font('Arial', size=9)
                            pdf.cell(70, 4, str(processo.nome_contribuinte[:35]), 1, align='L')
                            pdf.cell(22, 4, str(processo.numero), 1, align='C')
                            pdf.cell(20, 4, str(data_andamento_convertida), 1, align='C')
                            pdf.cell(76, 4, str(tipo_andamento[:35]), 1, align='C')
                            pdf.ln()
                    else:
                        armazena_andamentos_id.append(0) # Para não ocorrer erro de sequência vazia ao executar o max com a lista vazia.

                    armazena_andamentos_id.clear() # Limpa a lista de id para o próximo processo.


            # Totais
            pdf.set_font('Arial', size=9)
            pdf.cell(145, 10, txt=f'{total_registros_em_andamento} Registro(s)', ln=True)
            pdf.ln(5) # Pular 5 linhas

            # Daqui em diante o código é para criação do arquivo .pdf !!!

            # Salvar o PDF em um arquivo temporário
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            pdf.output(temp_file.name)
            temp_file.close()

            # Ler o conteúdo do arquivo temporário
            with open(temp_file.name, 'rb') as file:
                pdf_content = file.read()
            
            # Remover o arquivo temporario
            os.unlink(temp_file.name)

            # Criar uma resposta Http com o conteúdo do PDF
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="relatorio_geral.pdf"'

            return response
        
        else:
            response = HttpResponse('Nenhum município selecionado!')
            
            return response