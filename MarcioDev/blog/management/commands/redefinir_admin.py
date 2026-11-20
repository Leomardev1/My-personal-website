"""Cria ou redefine a senha de um superusuário a partir de variáveis de ambiente.

Variáveis:
  ADMIN_USERNAME   nome do superusuário (obrigatória)
  ADMIN_PASSWORD   nova senha (obrigatória)
  ADMIN_EMAIL      opcional; só usada ao criar um usuário novo

Se o usuário existir, só a senha muda (e ele passa a ser staff/superuser ativo).
Se não existir, é criado. Sem as variáveis definidas, o comando não faz nada.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Cria/redefine a senha do superusuário usando ADMIN_USERNAME e ADMIN_PASSWORD."

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME', '').strip()
        password = os.environ.get('ADMIN_PASSWORD', '')
        if not username or not password:
            self.stdout.write('ADMIN_USERNAME/ADMIN_PASSWORD não definidas; nada a fazer.')
            return

        User = get_user_model()
        user, criado = User.objects.get_or_create(
            username=username,
            defaults={'email': os.environ.get('ADMIN_EMAIL', '')},
        )
        user.is_staff = user.is_superuser = user.is_active = True
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(
            f"Superusuário '{username}' {'criado' if criado else 'atualizado'}."))
