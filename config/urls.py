# config/urls.py  —  master URL configuration for ZimLatestNews

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

# ------------------------------------------------------------------ sitemaps
from articles.sitemaps import ArticleSitemap, AuthorSitemap
from categories.sitemaps import CategorySitemap

sitemaps = {
    'articles':   ArticleSitemap,
    'authors':    AuthorSitemap,
    'categories': CategorySitemap,
}

# ------------------------------------------------------------------ handlers
from pages.views import handler404, handler500

handler404 = handler404
handler500 = handler500

# ------------------------------------------------------------------ admin branding
admin.site.site_header  = 'ZimLatestNews Admin'
admin.site.site_title   = 'ZimLatestNews'
admin.site.index_title  = 'Editorial Dashboard'

# ------------------------------------------------------------------ URL patterns
urlpatterns = [

    # Django admin
    path('admin/', admin.site.urls),

    # CKEditor image upload endpoint
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # ---- Your apps -------------------------------------------------------

    # Home + articles  (no prefix — lives at /)
    path('', include('articles.urls', namespace='articles')),

    # Category pages  →  /categories/sport/
    path('categories/', include('categories.urls', namespace='categories')),

    # Static pages, contact, newsletter  →  /pages/about/
    path('pages/', include('pages.urls', namespace='pages')),

    # Ad tracking endpoints  →  /ads/impression/3/
    path('ads/', include('ads.urls', namespace='ads')),

    # ---- SEO -------------------------------------------------------------

    # XML sitemap  →  /sitemap.xml
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    # Robots.txt is served as a static file — place it in /static/robots.txt
    # and WhiteNoise will serve it at /robots.txt automatically.

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# In production, WhiteNoise handles static files via middleware.
# Only add this in development:
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)