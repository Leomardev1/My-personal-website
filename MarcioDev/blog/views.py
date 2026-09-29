from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ComentarioForm, PostForm
from .models import Post


def portfolio(request):
	return render(request, 'blog/portfolio.html', {
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

	return render(request, 'blog/post_lista.html', {'pagina': pagina})


def post_detalhe(request, slug):
	post = get_object_or_404(
		Post.objects.prefetch_related('tags'),
		slug=slug,
		publicado=True,
	)

	if request.method == 'POST':
		formulario_comentario = ComentarioForm(request.POST)
		if formulario_comentario.is_valid():
			comentario = formulario_comentario.save(commit=False)
			comentario.post = post
			comentario.save()
			return redirect('blog:post_detalhe', slug=post.slug)
	else:
		formulario_comentario = ComentarioForm()

	comentarios = post.comentarios.filter(aprovado=True)
	return render(
		request,
		'blog/post_detalhe.html',
		{
			'post': post,
			'comentarios': comentarios,
			'formulario_comentario': formulario_comentario,
		},
	)


@login_required(login_url='login')
def post_criar(request):
	if request.method == 'POST':
		formulario = PostForm(request.POST)
		if formulario.is_valid():
			post = formulario.save(commit=False)
			post.publicado = True
			post.save()
			formulario.save_m2m()
			return redirect('blog:post_detalhe', slug=post.slug)
	else:
		formulario = PostForm()

	return render(request, 'blog/post_form.html', {'formulario': formulario})
