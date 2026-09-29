from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_lista, name='post_lista'),
    path('novo/', views.post_criar, name='post_criar'),
    path('<slug:slug>/', views.post_detalhe, name='post_detalhe'),
]
