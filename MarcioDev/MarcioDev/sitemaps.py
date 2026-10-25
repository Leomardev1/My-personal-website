from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Post


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return ["portfolio", "blog:post_lista"]

    def location(self, item):
        return reverse(item)


class PostSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return Post.objects.filter(publicado=True)