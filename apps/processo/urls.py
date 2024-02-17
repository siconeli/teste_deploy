from django.urls import path

from .views import ProcessoAdmView
from .views import ProcessoAdmArquivadoView
from .views import AndamentoAdmView
from .views import MesclarPDFsView
from .views import GerarRelatorio

from .views import ProcessoAdmCreate
from .views import AndamentoAdmCreate

from .views import ProcessoAdmUpdate
from .views import ProcessoAdmArquivadoUpdate
from .views import AndamentoAdmUpdate

from .views import ProcessoAdmDelete
from .views import ProcessoAdmArquivadoDelete
from .views import AndamentoAdmDelete

from .views import ProcessoAdmList
from .views import ProcessoAdmArquivadoList
from .views import AndamentoAdmList
from .views import AndamentoAdmListUpdate
from .views import ProcessoAdmExecutadoList
from .views import ProcessoAdmRecebidoList
from .views import ProcessoAdmAndamentoList
from .views import ProcessoAdmEncerradoList

from .views import Relatorio

urlpatterns = [

    ###### VIEW ######
    path('visualizar/processo-adm/<int:pk>/', ProcessoAdmView.as_view(), name='proc-adm-view'),
    path('visualizar/processo-adm-arquivado/<int:pk>/', ProcessoAdmArquivadoView.as_view(), name='proc-adm-arquivado-view'),
    path('visualizar/andamento-adm/<int:pk>/', AndamentoAdmView.as_view(), name='andamento-adm-view'),
    path('mesclar_pdf/', MesclarPDFsView.as_view(), name='mesclar_pdf'),
    path('gerar_relatorio/processo-adm/', GerarRelatorio.as_view(), name='proc-adm-report'),

    ###### CREATE ######
    path('cadastrar/processo-adm/', ProcessoAdmCreate.as_view(), name='proc-adm-create'), 
    path('cadastrar/andamento-adm/<int:pk>/', AndamentoAdmCreate.as_view(), name='andamento-adm-create'),

    ###### UPDATE ######
    path('editar/processo-adm/<int:pk>/', ProcessoAdmUpdate.as_view(), name='proc-adm-update'),
    path('editar/processo-adm-arquivado/<int:pk>/', ProcessoAdmArquivadoUpdate.as_view(), name='proc-adm-arquivado-update'),
    path('editar/andamento-adm/<int:pk>/', AndamentoAdmUpdate.as_view(), name='andamento-adm-update'),

    ###### DELETE ######
    path('deletar/processo-adm/<int:pk>/', ProcessoAdmDelete.as_view(), name='proc-adm-delete'),
    path('deletar/processo-adm-arquivado/<int:pk>/', ProcessoAdmArquivadoDelete.as_view(), name='proc-adm-arquivado-delete'),
    path('deletar/andamento-adm/<int:pk>/', AndamentoAdmDelete.as_view(), name='andamento-adm-delete'),

    ###### LIST ######
    path('listar/processo-adm/', ProcessoAdmList.as_view(), name='proc-adm-list'),
    path('listar/processo-adm-arquivado/', ProcessoAdmArquivadoList.as_view(), name='proc-adm-arquivado-list'),
    path('listar/andamento-adm/<int:pk>', AndamentoAdmList.as_view(), name='andamento-adm-list'),
    path('listar/andamento-adm-editar/<int:pk>', AndamentoAdmListUpdate.as_view(), name='andamento-adm-list-update'),
    path('listar/processo-adm-executado/', ProcessoAdmExecutadoList.as_view(), name='proc-adm-exec-list'),
    path('listar/processo-adm-recebido/', ProcessoAdmRecebidoList.as_view(), name='proc-adm-recebido-list'),
    path('listar/processo-adm-andamento/', ProcessoAdmAndamentoList.as_view(), name='proc-adm-andamento-list'),
    path('listar/processo-adm-encerrado/', ProcessoAdmEncerradoList.as_view(), name='proc-adm-encerrado-list'),

    ###### RELATÓRIO ######
    path('relatorio/processo-adm/', Relatorio.as_view(), name='proc-relatorio')
]