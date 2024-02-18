from django.db import models

from django.contrib.auth import get_user_model

from processo.models import Base

from processo.models import MunicipioAdm

class Funcionario(Base):
    nome = models.CharField(max_length=50)
    cargo = models.CharField(max_length=50)
    usuario = models.OneToOneField(get_user_model(), related_name='func', on_delete=models.PROTECT)

    def __str__(self):
        return f'Nome: {self.nome}'
    
class Atendimento(Base):
    municipio = models.ForeignKey(MunicipioAdm, on_delete=models.SET_NULL, null=True)
    data = models.DateField(null=True)
    cliente = models.CharField(max_length=50, null=True)
    descricao = models.TextField(max_length=10000, null=True)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.municipio, self.cliente, self.descricao, self.funcionario
    
