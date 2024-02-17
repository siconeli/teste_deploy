# O signals.py tem a função de inserir mensagens de logs no arquivo de log 'processo.log', toda vez que um usuário realizar o evento de Login ou Logout. 

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import logging

logger = logging.getLogger('auditoria_erros')

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f'Usuario - "{user}", realizou "Login" a partir do endereco IP: {request.META["REMOTE_ADDR"]}')

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f'Usuario - "{user}", realizou "Logout" a partir do endereco IP: {request.META["REMOTE_ADDR"]}')