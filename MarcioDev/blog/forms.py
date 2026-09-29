from django import forms

from .models import Comentario, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('titulo', 'resumo', 'conteudo', 'tags', 'publicado')
        widgets = {
            'resumo': forms.Textarea(attrs={'rows': 3}),
            'conteudo': forms.Textarea(attrs={'rows': 12}),
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ('nome', 'email', 'conteudo')
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 5}),
        }
