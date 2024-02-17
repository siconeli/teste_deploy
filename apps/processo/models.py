from django.db import models

from django.contrib.auth import get_user_model

from django.contrib.auth.models import User

class Auditoria(models.Model): #Logs de Create, Update, Delete
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    objeto_id = models.PositiveIntegerField()
    tipo_objeto = models.CharField(max_length=255) # processo administrativo, processo judiciario, andamento
    view = models.CharField(max_length=255)  # "create", "update", "delete"
    acao = models.CharField(max_length=255) # "create", "update", "delete"
    processo = models.CharField(max_length=255, blank=True, null=True)
    andamento = models.CharField(max_length=255, blank=True, null=True)
    campos_alterados = models.CharField(max_length=1000, blank=True, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-data_hora',)

class Base(models.Model): # Classe base, será herdada pelas outras classes - HERANÇA
    data_criacao = models.DateTimeField('data_criação', auto_now_add=True)
    usuario_criador = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    data_alteracao = models.DateTimeField('Alterado', auto_now=True)
    ativo = models.BooleanField('Ativo', default=True) # Ativo: 1 (True), Inativo: 0 (False)

    class Meta:  # Classe abstrata, não será instânciada.
        abstract = True

class Assunto(Base):
    assunto = models.CharField(max_length=100)

    def __str__(self):
        return self.assunto

class MunicipioAdm(Base):
    tipo = (
        ('Assessoria', 'Assessoria'), ('Sistema', 'Sistema')
    )
    nome = models.CharField(max_length=50)
    tipo_contrato = models.CharField(max_length=100, choices=tipo)
    contrato = models.CharField(max_length=50)
    brasao = models.ImageField(upload_to='brasoes/', default='brasaodefault.png') # Coloquei uma imagem em branco na pasta media para quando o usuario não fazer o upload de um brasão ao cadastrar um município, utilizar o default para não dar erro ao gerar o relatório.

    def __str__(self):
        return self.nome

class ProcessoAdm(Base):
    uf = (
        ('MS', 'MS'),
    )
    
    tipo_pessoas = (
        ('Física', 'Física'), ('Jurídica', 'Jurídica'),
    )

    numero = models.CharField(verbose_name='N°', max_length=10) # Número do processo  # unique=True (Para não permitir criar outro registro idêntico)
    municipio = models.ForeignKey(MunicipioAdm, on_delete=models.SET_NULL, null=True) # Município
    uf = models.CharField(max_length=2, choices=uf, default='MS') # UF 
    data_inicial = models.DateField(blank=True, null=True) # Data Inicial do Período do processo
    data_final = models.DateField(blank=True, null=True) # Data final do Período do processo
    data_div_ativa = models.DateField(blank=True, null=True) # Data dívida ativa
    valor_atributo = models.DecimalField(decimal_places=2, max_digits=11, blank=True, null=True)  # Valor do atributo
    valor_multa = models.DecimalField(decimal_places=2, max_digits=11, blank=True, null=True) # Valor da multa
    valor_credito = models.DecimalField(decimal_places=2, max_digits=11, blank=True, null=True) # Valor do crédito
    valor_atualizado = models.DecimalField(decimal_places=2, max_digits=11, blank=True, null=True) # Valor do atualizado
    data_valor_atualizado = models.DateField(blank=True, null=True) # Data valor atualizado
    nome_contribuinte = models.CharField(max_length=100)  # Nome / Razão Social
    tipo_pessoa = models.CharField(max_length=50, choices=tipo_pessoas) # Física / Jurídica # Utiliza choices(escolhas) para selecionar o tipo de pessoas
    documento = models.CharField(max_length=20, verbose_name='CPF/CNPJ') # CPF / CNPJ
    nome_fantasia = models.CharField(max_length=50, blank=True, null=True) # Nome Fantasia
    email = models.EmailField(max_length=50, blank=True, null=True) # E-mail
    endereco = models.CharField(max_length=150) # Rua
    complemento = models.CharField(max_length=50, blank=True, null=True) # Complemento
    municipio_contribuinte = models.CharField(max_length=50, blank=True, null=True) # Município Contribuinte
    uf_contribuinte = models.CharField(max_length=2, verbose_name='UF', blank=True, null=True) # UF Contribuinte
    cep = models.CharField(max_length=11, blank=True, null=True) # CEP
    telefone = models.CharField(max_length=20, blank=True, null=True) # Telefone
    celular = models.CharField(max_length=20, blank=True, null=True) # Celular

    def __str__(self):
        return f'{self.numero}'

class TipoAndamentoAdm(Base):
    tipo_andamento = models.CharField(max_length=100, verbose_name='Tipo de Andamento')

    def __str__(self):
        return self.tipo_andamento
    
class AndamentoAdm(Base):
    # Choices
    situacao = (
        ('Sem Pagamento', 'Sem Pagamento'), ('Com Pagamento', 'Com Pagamento'),
    )

    localizacao = (
        ('Na Aeg', 'Na Aeg'), ('No Município', 'No Município'), ('No Fórum', 'No Fórum'),
    )

    processo = models.ForeignKey(ProcessoAdm, on_delete=models.CASCADE) # Relacionamento 'One to Many' (um para muitos)
    data_andamento = models.DateField(verbose_name='Data do Andamento')
    tipo_andamento = models.ForeignKey(TipoAndamentoAdm, on_delete=models.SET_NULL, null=True) 
    situacao_pagamento = models.CharField(max_length=100, choices=situacao, blank=True, null=True) 
    valor_pago = models.DecimalField(decimal_places=2, max_digits=11, blank=True, null=True)
    data_prazo = models.DateField(blank=True, null=True)
    funcionario = models.CharField(max_length=50, blank=True, null=True)
    localizacao_processo = models.CharField(max_length=50, choices=localizacao, blank=True, null=True)
    data_recebimento = models.DateField(blank=True, null=True)
    # complemento = models.CharField(max_length=150, blank=True, null=True)
    assunto = models.ForeignKey(Assunto, on_delete=models.SET_NULL, null=True, blank=True)
    arquivo = models.FileField(upload_to='arquivo/', verbose_name='Arquivo', blank=True) 

    def __str__(self):
        return f'Processo: {self.processo} | Andamento: {self.tipo_andamento} ID: {self.id} | Pagamento: {self.situacao_pagamento} | Arquivo: {self.arquivo} | Ativo: {self.ativo}'

