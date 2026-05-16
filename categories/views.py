from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.core.paginator import Paginator

from .models import Category
from articles.models import Article
from ads.models import AdUnit


class CategoryListView(View):
    """All categories overview page — like a sitemap of topics."""
    template_name = 'list.html'

    def get(self, request):
        # Top-level only; children nested under them
        top_level = Category.objects.filter(
            parent=None, is_active=True
        ).prefetch_related('children').order_by('nav_order', 'name')

        context = {
            'top_level': top_level,
        }
        return render(request, self.template_name, context)


class CategoryDetailView(View):
    """Landing page for a single category — shows articles, sub-cats, hero."""
    template_name = 'detail.html'
    paginate_by = 12

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug, is_active=True)

        # Pull articles from this category AND any sub-categories
        cat_ids = [category.pk] + list(category.children.values_list('pk', flat=True))

        articles = Article.objects.filter(
            status=Article.Status.PUBLISHED,
            category__in=cat_ids,
        ).select_related('author', 'category').order_by('-published_at')

        # Hero — most recent featured, else most recent
        hero = articles.filter(
            priority__in=[Article.Priority.FEATURED, Article.Priority.EDITOR, Article.Priority.BREAKING]
        ).first() or articles.first()

        # Remaining articles for the grid (exclude hero)
        grid = articles.exclude(pk=hero.pk if hero else 0)

        paginator = Paginator(grid, self.paginate_by)
        page_obj  = paginator.get_page(request.GET.get('page'))

        # Breadcrumb ancestors
        ancestors = category.get_ancestors()

        context = {
            'category':  category,
            'hero':      hero,
            'page_obj':  page_obj,
            'ancestors': ancestors,
            'sub_cats':  category.children.filter(is_active=True).order_by('nav_order'),
            'total':     articles.count(),
            'leaderboard': AdUnit.objects.filter(
                position=AdUnit.Position.LEADERBOARD_TOP, is_active=True
            ).first(),
        }
        return render(request, self.template_name, context)