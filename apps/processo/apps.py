from django.apps import AppConfig

class ProcessoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.processo'

    # Para o tratamento de sinal de Login e Logout ser executado e registrar mensagem de log no arquivo de log 'processo.log'
    def ready(self):
        import apps.processo.signals
