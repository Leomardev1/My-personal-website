from django.contrib import admin

from .forms import AdminLoginForm
from .models import Comentario, Post, Tag

# O login do admin usa o mesmo limite de tentativas que /accounts/login/.
admin.site.login_form = AdminLoginForm


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
    actions = ['aprovar_comentarios']

    @admin.action(description='Aprovar comentários selecionados')
    def aprovar_comentarios(self, request, queryset):
        total = queryset.update(aprovado=True)
        self.message_user(request, f'{total} comentário(s) aprovado(s).')
