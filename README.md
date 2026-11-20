# My personal website

Portfolio e blog pessoal de Leomar, feito com Django.

**Site:** https://my-personal-website-3-5ggz.onrender.com

- Página de apresentação (portfolio)
- Blog com posts, tags e comentários moderados
- Painel de administração do Django em `/admin/`

## Correr no computador

Dentro da pasta `MarcioDev`:

```bash
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

O ficheiro `.env` activa o modo de desenvolvimento (`DEBUG=True`) e não vai para o git.
No PowerShell, o segundo comando é `Copy-Item .env.example .env`.

Para correr os testes:

```bash
python manage.py test
```

## Produção (Render)

Variáveis de ambiente a definir no painel do serviço:

| Variável | Obrigatória | Para que serve |
|---|---|---|
| `SECRET_KEY` | Sim | Chave secreta do Django. Tem de ser longa e aleatória; sem ela o deploy falha. |
| `DATABASE_URL` | Recomendada | Ligação ao PostgreSQL. Sem ela usa-se SQLite, que o Render apaga a cada deploy. |
| `SITE_HOST` | Não | Só com domínio próprio (ex.: `meusite.com`). |

Comandos do serviço (pasta raiz `MarcioDev`):

- Build: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
- Start: `gunicorn MarcioDev.wsgi:application`

## Notas

- Os comentários só aparecem no blog depois de aprovados em `/admin/` (acção "Aprovar comentários selecionados").
- Só utilizadores com a permissão "Can add post" (ou superutilizadores) criam posts em `/posts/novo/`.
- Depois de 5 logins falhados, o endereço IP fica bloqueado durante 15 minutos.
