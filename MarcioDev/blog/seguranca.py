"""Limite de tentativas de login falhadas.

Protege /accounts/login/ e /admin/login/ contra a adivinhação de senhas: depois de
MAX_FALHAS tentativas erradas vindas do mesmo endereço IP, os formulários de login
(ver blog/forms.py) recusam esse endereço até a janela de tempo terminar.

Os contadores ficam na cache do Django, que por omissão vive na memória de cada
processo: chega para um único worker do gunicorn, como no plano gratuito do Render.
"""
import hashlib
import time

from django.contrib.auth.signals import user_login_failed
from django.core.cache import cache
from django.dispatch import receiver

MAX_FALHAS = 5
JANELA_SEGUNDOS = 15 * 60
MENSAGEM_BLOQUEIO = 'Muitas tentativas de login falhadas. Tente novamente em alguns minutos.'


def ip_do_cliente(request):
    # Atrás do proxy do Render, REMOTE_ADDR é o endereço do proxy; o do visitante
    # chega nos cabeçalhos. Quem conseguir falsificá-los só contorna este limite,
    # não consegue bloquear outra pessoa sem saber o IP dela.
    encaminhado = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
    return (
        request.META.get('HTTP_CF_CONNECTING_IP')
        or encaminhado
        or request.META.get('REMOTE_ADDR', '')
    )


def _chave(request):
    return 'login-falhas:' + hashlib.sha256(ip_do_cliente(request).encode()).hexdigest()


def _estado(request):
    """Devolve (falhas, expira_em) da janela em curso, ou (0, None) se não houver."""
    falhas, expira_em = cache.get(_chave(request), (0, None))
    if expira_em is None or expira_em <= time.time():
        return 0, None
    return falhas, expira_em


def login_bloqueado(request):
    if request is None:
        return False
    falhas, _ = _estado(request)
    return falhas >= MAX_FALHAS


def registar_falha(request):
    falhas, expira_em = _estado(request)
    agora = time.time()
    if expira_em is None:
        # A janela conta a partir da primeira falha e não é prolongada pelas seguintes.
        expira_em = agora + JANELA_SEGUNDOS
    cache.set(_chave(request), (falhas + 1, expira_em), timeout=max(1, int(expira_em - agora)))


@receiver(user_login_failed)
def _contar_login_falhado(sender, credentials, request=None, **kwargs):
    if request is not None:
        registar_falha(request)
