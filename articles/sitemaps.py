from django.contrib.sitemaps import Sitemap
from .models import Article, Author
 
 
class ArticleSitemap(Sitemap):
    changefreq = 'daily'
    priority   = 0.9
    protocol   = 'https'
 
    def items(self):
        return Article.objects.filter(status=Article.Status.PUBLISHED).order_by('-published_at')
 
    def lastmod(self, obj):
        return obj.updated_at
 
    def location(self, obj):
        return obj.get_absolute_url()
 
 
class AuthorSitemap(Sitemap):
    changefreq = 'weekly'
    priority   = 0.6
    protocol   = 'https'
 
    def items(self):
        return Author.objects.filter(is_active=True)
 
    def lastmod(self, obj):
        return obj.updated_at
 
    def location(self, obj):
        return obj.get_absolute_url()