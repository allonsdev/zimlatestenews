from django.contrib.sitemaps import Sitemap
from .models import Category

class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()