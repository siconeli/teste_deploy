# Generated by Django 5.0.1 on 2024-02-05 18:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('processo', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='data_criação')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Alterado')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('nome', models.CharField(max_length=50)),
                ('cargo', models.CharField(max_length=50)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='func', to=settings.AUTH_USER_MODEL)),
                ('usuario_criador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Atendimento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='data_criação')),
                ('data_alteracao', models.DateTimeField(auto_now=True, verbose_name='Alterado')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('data', models.DateField(null=True)),
                ('cliente', models.CharField(max_length=50, null=True)),
                ('descricao', models.TextField(max_length=10000, null=True)),
                ('municipio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='processo.municipioadm')),
                ('usuario_criador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('funcionario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='rat.funcionario')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
