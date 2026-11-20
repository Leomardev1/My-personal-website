from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import AuthenticationForm

from .models import Comentario, Post
from .seguranca import MENSAGEM_BLOQUEIO, login_bloqueado

# Comentários por aprovar que cada post aceita: trava envios em massa.
MAX_COMENTARIOS_PENDENTES = 30


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('titulo', 'resumo', 'conteudo', 'tags', 'publicado')
        widgets = {
            'resumo': forms.Textarea(attrs={'rows': 3}),
            'conteudo': forms.Textarea(attrs={'rows': 12}),
        }
        help_texts = {
            'publicado': 'Desmarque para salvar como rascunho.',
        }


class ComentarioForm(forms.ModelForm):
    # Campo-armadilha: fica escondido por CSS e só programas automáticos o preenchem.
    website = forms.CharField(
        required=False,
        label='Deixe este campo vazio',
        widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}),
    )

    class Meta:
        model = Comentario
        fields = ('nome', 'email', 'conteudo')
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 5}),
        }
        help_texts = {
            'email': 'Não será publicado.',
        }

    def __init__(self, *args, post=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.post = post

    @property
    def parece_spam(self):
        return bool(self.cleaned_data.get('website'))

    def clean(self):
        dados = super().clean()
        if self.post is not None and not dados.get('website'):
            pendentes = self.post.comentarios.filter(aprovado=False).count()
            if pendentes >= MAX_COMENTARIOS_PENDENTES:
                raise forms.ValidationError(
                    'Há muitos comentários aguardando aprovação neste post. '
                    'Tente novamente mais tarde.'
                )
        return dados


class LimiteDeTentativasMixin:
    """Recusa o login, sem chegar a verificar a senha, enquanto o IP estiver bloqueado."""

    def clean(self):
        if login_bloqueado(self.request):
            raise forms.ValidationError(MENSAGEM_BLOQUEIO, code='bloqueado')
        return super().clean()


class LoginForm(LimiteDeTentativasMixin, AuthenticationForm):
    pass


class AdminLoginForm(LimiteDeTentativasMixin, AdminAuthenticationForm):
    pass
