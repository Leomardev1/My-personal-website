from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Post


class ComentarioAprovadoTest(TestCase):
    def test_comentario_salva_e_ja_aparece_aprovado(self):
        post = Post.objects.create(
            titulo='Post de teste',
            conteudo='Conteudo de teste',
            publicado=True,
        )
        post.slug = 'post-de-teste'
        post.save(update_fields=['slug'])

        response = self.client.post(
            reverse('blog:post_detalhe', kwargs={'slug': post.slug}),
            {
                'nome': 'Maria',
                'email': 'maria@email.com',
                'conteudo': 'Comentario de teste',
            },
        )

        self.assertEqual(response.status_code, 302)
        comentario = post.comentarios.get()
        self.assertTrue(comentario.aprovado)
        self.assertEqual(comentario.conteudo, 'Comentario de teste')


class PortfolioPageTest(TestCase):
    def test_homepage_exibe_portfolio(self):
        response = self.client.get(reverse('portfolio'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Leomar')
        self.assertContains(response, 'Python')


class PostCriacaoTest(TestCase):
    def test_post_criar_exige_login(self):
        response = self.client.get(reverse('blog:post_criar'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_novo_post_fica_publicado_por_padrao(self):
        User = get_user_model()
        User.objects.create_user(username='admin', password='senha123')
        self.client.login(username='admin', password='senha123')

        response = self.client.post(
            reverse('blog:post_criar'),
            {
                'titulo': 'Novo post',
                'resumo': 'Resumo do post',
                'conteudo': 'Conteudo completo do post',
            },
        )

        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(titulo='Novo post')
        self.assertTrue(post.publicado)

    def test_usuario_logado_pode_criar_post(self):
        User = get_user_model()
        User.objects.create_user(username='admin', password='senha123')
        self.client.login(username='admin', password='senha123')

        response = self.client.post(
            reverse('blog:post_criar'),
            {
                'titulo': 'Novo post',
                'resumo': 'Resumo do post',
                'conteudo': 'Conteudo completo do post',
                'publicado': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(titulo='Novo post').exists())
