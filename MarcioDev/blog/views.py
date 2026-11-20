from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import Truncator

from .forms import ComentarioForm, PostForm
from .models import Post

TITULO_DO_SITE = 'Leomar | Desenvolvedor Python e Django'
DESCRICAO_DO_SITE = (
    'Portfolio pessoal de Leomar, desenvolvedor focado em Python, Django e interfaces web claras.'
)
PERFIS_SOCIAIS = [
    'https://github.com/Leomardev1',
    'https://www.instagram.com/leomardev1/',
]


def portfolio(request):
    return render(request, 'blog/portfolio.html', {
        'pagina_titulo': TITULO_DO_SITE,
        'pagina_descricao': DESCRICAO_DO_SITE,
        # Dados estruturados: dizem ao Google quem é a pessoa por trás do site.
        'dados_estruturados': {
            '@context': 'https://schema.org',
            '@type': 'Person',
            'name': settings.SITE_NAME,
            'url': f'{settings.SITE_URL}/',
            'jobTitle': 'Desenvolvedor Python e Django',
            'knowsAbout': ['Python', 'Django', 'HTML', 'CSS', 'JavaScript'],
            'sameAs': PERFIS_SOCIAIS,
        },
        'project_list': [
            {
                'name': 'Blog pessoal',
                'stack': 'Django • Python • HTML',
                'description': 'Um espaço simples para publicar ideias, experiências e pequenos aprendizados com uma interface limpa e direta.',
            },
            {
                'name': 'Portfolio pessoal',
                'stack': 'Django • CSS • UX',
                'description': 'Uma página de apresentação pensada para comunicar quem sou, o que faço e como minha trajetória está evoluindo no desenvolvimento web.',
            },
            {
                'name': 'Área de estudo',
                'stack': 'Aprendizado contínuo',
                'description': 'Experimentos, melhorias de interface e pequenos projetos usados para fortalecer lógica, design e produtividade.',
            },
        ],
    })


def post_lista(request):
    posts_publicados = Post.objects.filter(publicado=True).prefetch_related('tags')
    paginator = Paginator(posts_publicados, 5)
    pagina = paginator.get_page(request.GET.get('page'))

    titulo = f'Posts | {settings.SITE_NAME}'
    canonica = settings.SITE_URL + reverse('blog:post_lista')
    if pagina.number > 1:
        # Cada página da listagem é canónica de si própria.
        titulo = f'Posts, página {pagina.number} | {settings.SITE_NAME}'
        canonica += f'?page={pagina.number}'

    return render(request, 'blog/post_lista.html', {
        'pagina': pagina,
        'pagina_titulo': titulo,
        'pagina_descricao': 'Artigos e reflexões de Leomar sobre desenvolvimento, aprendizado e produção digital.',
        'pagina_canonical': canonica,
    })


def post_detalhe(request, slug):
    post = get_object_or_404(
        Post.objects.prefetch_related('tags'),
        slug=slug,
        publicado=True,
    )

    if request.method == 'POST':
        formulario_comentario = ComentarioForm(request.POST, post=post)
        if formulario_comentario.is_valid():
            # Quem preenche o campo-armadilha recebe a mesma resposta, mas nada é gravado.
            if not formulario_comentario.parece_spam:
                comentario = formulario_comentario.save(commit=False)
                comentario.post = post
                comentario.save()
            messages.success(request, 'Comentário enviado! Ele aparece aqui depois de aprovado.')
            return redirect(post)
    else:
        formulario_comentario = ComentarioForm(post=post)

    descricao = Truncator(' '.join((post.resumo or post.conteudo).split())).words(20)
    url_do_post = settings.SITE_URL + post.get_absolute_url()

    return render(
        request,
        'blog/post_detalhe.html',
        {
            'post': post,
            'comentarios': post.comentarios.filter(aprovado=True),
            'formulario_comentario': formulario_comentario,
            'pagina_titulo': f'{post.titulo} | {settings.SITE_NAME}',
            'pagina_descricao': descricao,
            'pagina_tipo': 'article',
            'dados_estruturados': {
                '@context': 'https://schema.org',
                '@type': 'BlogPosting',
                'headline': post.titulo,
                'description': descricao,
                'datePublished': post.criado_em,
                'dateModified': post.atualizado_em,
                'mainEntityOfPage': url_do_post,
                'author': {
                    '@type': 'Person',
                    'name': settings.SITE_NAME,
                    'url': f'{settings.SITE_URL}/',
                },
            },
        },
    )


@login_required(login_url='login')
@permission_required('blog.add_post', raise_exception=True)
def post_criar(request):
    if request.method == 'POST':
        formulario = PostForm(request.POST)
        if formulario.is_valid():
            post = formulario.save()
            if post.publicado:
                return redirect(post)
            # Um rascunho não tem página pública: volta-se à lista com um aviso.
            messages.info(
                request,
                f'Rascunho "{post.titulo}" salvo. Publique-o no painel de administração.',
            )
            return redirect('blog:post_lista')
    else:
        formulario = PostForm()

    return render(request, 'blog/post_form.html', {
        'formulario': formulario,
        'pagina_titulo': f'Criar post | {settings.SITE_NAME}',
        'pagina_noindex': True,
    })


def favicon(request):
    # Os browsers pedem /favicon.ico por omissão; o ícone verdadeiro é um SVG estático.
    return redirect(static('blog/favicon.svg'))
