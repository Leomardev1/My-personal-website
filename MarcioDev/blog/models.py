from django.db import models
from django.utils.text import slugify


def gerar_slug_unico(instancia, valor):
    # Converte o nome ou titulo em um texto adequado para usar na URL.
    slug_base = slugify(valor)
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
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    resumo = models.TextField(blank=True)
    conteudo = models.TextField()
    # Um post pode ter varias tags, e uma tag pode estar em varios posts.
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    publicado = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def save(self, *args, **kwargs):
        # O slug permite enderecos como /posts/meu-primeiro-post/.
        if not self.slug:
            self.slug = gerar_slug_unico(self, self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    # Ao excluir um post, seus comentarios tambem sao excluidos.
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    conteudo = models.TextField()
    # Comentarios novos sao exibidos imediatamente no blog.
    aprovado = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']
        verbose_name = 'comentario'
        verbose_name_plural = 'comentarios'

    def __str__(self):
        return f'Comentario de {self.nome} em {self.post}'
