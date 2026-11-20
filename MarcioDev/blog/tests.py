from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .forms import MAX_COMENTARIOS_PENDENTES
from .models import TAMANHO_MAXIMO_COMENTARIO, Comentario, Post
from .seguranca import MAX_FALHAS, MENSAGEM_BLOQUEIO

SENHA = 'senha-de-teste-1234'


def criar_post(**campos):
    dados = {'titulo': 'Post de teste', 'conteudo': 'Conteudo de teste', 'publicado': True}
    dados.update(campos)
    return Post.objects.create(**dados)


def criar_utilizador(username, pode_criar_posts=False):
    utilizador = get_user_model().objects.create_user(username=username, password=SENHA)
    if pode_criar_posts:
        utilizador.user_permissions.add(Permission.objects.get(codename='add_post'))
    return utilizador


class PortfolioPageTest(TestCase):
    def test_homepage_exibe_portfolio(self):
        response = self.client.get(reverse('portfolio'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Leomar')
        self.assertContains(response, 'Python')

    def test_homepage_tem_tags_para_motores_de_busca(self):
        response = self.client.get(reverse('portfolio'))

        self.assertContains(response, f'<link rel="canonical" href="{settings.SITE_URL}/">', html=True)
        self.assertContains(response, 'property="og:title"')
        self.assertContains(response, '<script type="application/ld+json">')
        self.assertContains(response, '"@type": "Person"')
        self.assertNotContains(response, 'noindex')


class PostListaTest(TestCase):
    def test_lista_mostra_so_posts_publicados(self):
        criar_post(titulo='Post visivel')
        criar_post(titulo='Rascunho escondido', publicado=False)

        response = self.client.get(reverse('blog:post_lista'))

        self.assertContains(response, 'Post visivel')
        self.assertNotContains(response, 'Rascunho escondido')

    def test_cada_pagina_da_lista_tem_o_seu_url_canonico(self):
        for numero in range(6):
            criar_post(titulo=f'Post {numero}')
        url = settings.SITE_URL + reverse('blog:post_lista')

        primeira = self.client.get(reverse('blog:post_lista'))
        segunda = self.client.get(reverse('blog:post_lista'), {'page': 2})

        self.assertContains(primeira, f'<link rel="canonical" href="{url}">', html=True)
        self.assertContains(segunda, f'<link rel="canonical" href="{url}?page=2">', html=True)


class PostDetalheTest(TestCase):
    def test_post_publicado_tem_dados_estruturados(self):
        post = criar_post(titulo='Aprendendo Django')

        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"@type": "BlogPosting"')
        self.assertContains(response, 'property="og:type" content="article"')

    def test_rascunho_nao_tem_pagina_publica(self):
        post = criar_post(publicado=False)

        response = self.client.get(post.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_titulo_nao_consegue_fechar_a_tag_de_dados_estruturados(self):
        post = criar_post(titulo='</script><script>alert(1)</script>')

        response = self.client.get(post.get_absolute_url())

        self.assertNotContains(response, '</script><script>alert(1)')


class ComentarioTest(TestCase):
    def setUp(self):
        self.post = criar_post()
        self.url = self.post.get_absolute_url()
        self.dados = {
            'nome': 'Maria',
            'email': 'maria@email.com',
            'conteudo': 'Comentario de teste',
        }

    def test_comentario_fica_a_aguardar_aprovacao(self):
        response = self.client.post(self.url, self.dados, follow=True)

        comentario = self.post.comentarios.get()
        self.assertFalse(comentario.aprovado)
        self.assertContains(response, 'depois de aprovado')
        self.assertNotContains(response, 'Comentario de teste')

    def test_comentario_aprovado_aparece_no_post(self):
        self.client.post(self.url, self.dados)
        self.post.comentarios.update(aprovado=True)

        response = self.client.get(self.url)

        self.assertContains(response, 'Comentario de teste')

    def test_campo_armadilha_descarta_o_comentario_sem_avisar(self):
        response = self.client.post(self.url, {**self.dados, 'website': 'http://spam.example'})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comentario.objects.exists())

    def test_comentario_demasiado_longo_e_recusado(self):
        self.dados['conteudo'] = 'a' * (TAMANHO_MAXIMO_COMENTARIO + 1)

        response = self.client.post(self.url, self.dados)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comentario.objects.exists())

    def test_post_recusa_comentarios_quando_ha_muitos_por_aprovar(self):
        Comentario.objects.bulk_create(
            Comentario(post=self.post, nome='x', email='x@email.com', conteudo='pendente')
            for _ in range(MAX_COMENTARIOS_PENDENTES)
        )

        response = self.client.post(self.url, self.dados)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aguardando aprovação')
        self.assertEqual(self.post.comentarios.count(), MAX_COMENTARIOS_PENDENTES)


class PostCriacaoTest(TestCase):
    def setUp(self):
        self.url = reverse('blog:post_criar')
        self.dados = {
            'titulo': 'Novo post',
            'resumo': 'Resumo do post',
            'conteudo': 'Conteudo completo do post',
            'publicado': 'on',
        }

    def test_post_criar_exige_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_utilizador_sem_permissao_nao_cria_posts(self):
        criar_utilizador('visitante')
        self.client.login(username='visitante', password=SENHA)

        response = self.client.post(self.url, self.dados)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Post.objects.exists())

    def test_autor_publica_post(self):
        criar_utilizador('autor', pode_criar_posts=True)
        self.client.login(username='autor', password=SENHA)

        response = self.client.post(self.url, self.dados)

        post = Post.objects.get(titulo='Novo post')
        self.assertTrue(post.publicado)
        self.assertRedirects(response, post.get_absolute_url())

    def test_sem_marcar_publicado_o_post_fica_como_rascunho(self):
        criar_utilizador('autor', pode_criar_posts=True)
        self.client.login(username='autor', password=SENHA)
        del self.dados['publicado']

        response = self.client.post(self.url, self.dados, follow=True)

        post = Post.objects.get(titulo='Novo post')
        self.assertFalse(post.publicado)
        self.assertRedirects(response, reverse('blog:post_lista'))
        self.assertContains(response, 'Rascunho')
        self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 404)

    def test_titulo_sem_letras_recebe_um_slug_valido(self):
        criar_utilizador('autor', pode_criar_posts=True)
        self.client.login(username='autor', password=SENHA)

        self.client.post(self.url, {**self.dados, 'titulo': '🚀🚀🚀'})
        self.client.post(self.url, {**self.dados, 'titulo': '!!!'})

        self.assertEqual(
            list(Post.objects.order_by('pk').values_list('slug', flat=True)),
            ['post', 'post-2'],
        )
        self.assertEqual(self.client.get(reverse('blog:post_lista')).status_code, 200)


class SitemapRobotsTest(TestCase):
    def test_sitemap_lista_os_posts_publicados(self):
        publicado = criar_post(titulo='Post no sitemap')
        rascunho = criar_post(titulo='Rascunho fora do sitemap', publicado=False)

        response = self.client.get('/sitemap.xml')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<loc>{settings.SITE_URL}/</loc>')
        self.assertContains(response, f'<loc>{settings.SITE_URL}{publicado.get_absolute_url()}</loc>')
        self.assertContains(response, '<lastmod>')
        self.assertNotContains(response, rascunho.slug)

    def test_robots_aponta_para_o_sitemap(self):
        response = self.client.get('/robots.txt')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'Disallow: /admin/')
        self.assertContains(response, f'Sitemap: {settings.SITE_URL}/sitemap.xml')

    def test_favicon_redirecciona_para_o_icone(self):
        response = self.client.get('/favicon.ico')

        self.assertEqual(response.status_code, 302)
        self.assertIn('blog/favicon', response.url)


class LoginTest(TestCase):
    def setUp(self):
        # Os contadores de tentativas vivem na cache, que é partilhada entre testes.
        cache.clear()
        self.addCleanup(cache.clear)
        criar_utilizador('autor')
        self.url = reverse('login')

    def errar_senha(self, url, vezes=MAX_FALHAS, **extra):
        for _ in range(vezes):
            self.client.post(url, {'username': 'autor', 'password': 'senha-errada'}, **extra)

    def test_pagina_de_login_fica_fora_dos_motores_de_busca(self):
        response = self.client.get(self.url)

        self.assertContains(response, '<meta name="robots" content="noindex">', html=True)
        self.assertNotContains(response, 'rel="canonical"')

    def test_login_com_senha_certa(self):
        response = self.client.post(self.url, {'username': 'autor', 'password': SENHA})

        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)
        self.assertIn('_auth_user_id', self.client.session)

    def test_poucas_falhas_nao_bloqueiam(self):
        self.errar_senha(self.url, vezes=MAX_FALHAS - 1)

        self.client.post(self.url, {'username': 'autor', 'password': SENHA})

        self.assertIn('_auth_user_id', self.client.session)

    def test_login_bloqueado_depois_de_varias_falhas(self):
        self.errar_senha(self.url)

        response = self.client.post(self.url, {'username': 'autor', 'password': SENHA})

        self.assertContains(response, MENSAGEM_BLOQUEIO)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_bloqueio_e_por_endereco_ip(self):
        self.errar_senha(self.url, HTTP_X_FORWARDED_FOR='203.0.113.7')

        self.client.post(
            self.url,
            {'username': 'autor', 'password': SENHA},
            HTTP_X_FORWARDED_FOR='198.51.100.20',
        )

        self.assertIn('_auth_user_id', self.client.session)

    def test_admin_partilha_o_mesmo_limite(self):
        self.errar_senha(reverse('admin:login'))

        response = self.client.post(self.url, {'username': 'autor', 'password': SENHA})

        self.assertContains(response, MENSAGEM_BLOQUEIO)

    def test_admin_mostra_o_aviso_de_bloqueio(self):
        self.errar_senha(self.url)

        response = self.client.post(
            reverse('admin:login'),
            {'username': 'autor', 'password': SENHA},
        )

        self.assertContains(response, MENSAGEM_BLOQUEIO)

    def test_recuperacao_de_senha_por_email_foi_retirada(self):
        response = self.client.get('/accounts/password_reset/')

        self.assertEqual(response.status_code, 404)
