from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Post


class SitemapDoSite(Sitemap):
    protocol = "https"

    def get_domain(self, site=None):
        # Usa sempre o domínio canónico, mesmo que o pedido chegue por outro endereço.
        return settings.SITE_HOST


class StaticViewSitemap(SitemapDoSite):
    priority = 1.0
    changefreq = "monthly"

    def items(self):
        return ["portfolio", "blog:post_lista"]

    def location(self, item):
        return reverse(item)


class PostSitemap(SitemapDoSite):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return Post.objects.filter(publicado=True)

    def lastmod(self, post):
        return post.atualizado_em
