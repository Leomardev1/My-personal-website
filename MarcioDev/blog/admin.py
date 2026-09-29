from django.contrib import admin

from .models import Comentario, Post, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    prepopulated_fields = {'slug': ('nome',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'publicado', 'criado_em', 'atualizado_em')
    list_filter = ('publicado', 'tags')
    search_fields = ('titulo', 'conteudo')
    prepopulated_fields = {'slug': ('titulo',)}
    filter_horizontal = ('tags',)


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'post', 'aprovado', 'criado_em')
    list_filter = ('aprovado', 'criado_em')
    search_fields = ('nome', 'email', 'conteudo')
