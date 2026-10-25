"""
URL configuration for MarcioDev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView

from blog import views as blog_views
from .sitemaps import PostSitemap, StaticViewSitemap

sitemaps = {"static": StaticViewSitemap, "posts": PostSitemap}

def google_verification(request):
    return HttpResponse(
        "google-site-verification: google8226808ef9ac6c65.html",
        content_type="text/html",
    )

urlpatterns = [
    path('', blog_views.portfolio, name='portfolio'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('posts/', include('blog.urls')),
    path("google8226808ef9ac6c65.html", google_verification),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps},
         name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(
        template_name="robots.txt", content_type="text/plain"))
]
