# Generated by Django 5.0.1 on 2024-02-15 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo', '0013_rename_arquivo_andamentoadm_arquivo1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='andamentoadm',
            name='arquivo2',
        ),
        migrations.RemoveField(
            model_name='andamentoadm',
            name='arquivo3',
        ),
        migrations.AlterField(
            model_name='andamentoadm',
            name='arquivo1',
            field=models.FileField(blank=True, upload_to='arquivo/', verbose_name='Arquivo1'),
        ),
    ]
