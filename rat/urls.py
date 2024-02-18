from django.urls import path
from .views import (
    AtendimentoView,
    AtendimentoCreate,
    AtendimentoUpdate,
    AtendimentoDelete,
    AtendimentoList,
    # Pdf,
)

urlpatterns = [
    ###### VIEW ######
    path('visualizar/atendimento/<int:pk>/', AtendimentoView.as_view(), name='atendimento-view'),

    ###### CREATE ######
    path('cadastrar/atendimento/', AtendimentoCreate.as_view(), name='atendimento-create'),

    ###### UPDATE ######
    path('editar/atendimento/<int:pk>', AtendimentoUpdate.as_view(), name='atendimento-update'),

    ###### DELETE ######
    path('deletar/atendimento/<int:pk>/', AtendimentoDelete.as_view(), name='atendimento-delete'),

    ###### LIST ######
    path('listar/atendimento/', AtendimentoList.as_view(), name='atendimento-list'),

    # ###### RELATÓRIO ######
    # path('relatorio/atendimento/', Pdf.as_view(), name='atendimento-relatorio'),
]