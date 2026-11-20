from django.db import models
from django.urls import reverse
from django.utils.text import slugify

# Limite de caracteres de um comentário (validado no formulário).
TAMANHO_MAXIMO_COMENTARIO = 2000


def gerar_slug_unico(instancia, valor):
    # Converte o nome ou titulo em um texto adequado para usar na URL.
    # Titulos so com simbolos ou emojis nao geram slug: usa-se o nome do modelo.
    slug_base = slugify(valor) or instancia._meta.model_name
    slug = slug_base
    contador = 2
    modelo = instancia.__class__

    # Se o slug ja existir, acrescenta um numero ate encontrar um valor livre.
    while modelo.objects.filter(slug=slug).exclude(pk=instancia.pk).exists():
        slug = f'{slug_base}-{contador}'
        contador += 1

    return slug


class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def save(self, *args, **kwargs):
        # O slug e criado apenas no primeiro salvamento para permanecer estavel.
        if not self.slug:
            self.slug = gerar_slug_unico(self, self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Post(models.Model):
    titulo = models.CharField('título', max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    resumo = models.TextField(blank=True)
    conteudo = models.TextField('conteúdo')
    # Um post pode ter varias tags, e uma tag pode estar em varios posts.
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    # Desmarcado, o post fica como rascunho: nao aparece no blog nem no sitemap.
    publicado = models.BooleanField(default=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def save(self, *args, **kwargs):
        # O slug permite enderecos como /posts/meu-primeiro-post/.
        if not self.slug:
            self.slug = gerar_slug_unico(self, self.titulo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        # Usado pelo sitemap e pelo botao "Ver no site" do admin.
        return reverse('blog:post_detalhe', kwargs={'slug': self.slug})

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    # Ao excluir um post, seus comentarios tambem sao excluidos.
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    nome = models.CharField(max_length=100)
    email = models.EmailField('e-mail')
    conteudo = models.TextField('comentário', max_length=TAMANHO_MAXIMO_COMENTARIO)
    # Comentarios novos so aparecem no blog depois de aprovados no admin.
    aprovado = models.BooleanField(default=False)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        ordering = ['criado_em']
        verbose_name = 'comentário'
        verbose_name_plural = 'comentários'

    def __str__(self):
        return f'Comentário de {self.nome} em {self.post}'
