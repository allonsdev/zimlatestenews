from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib import messages
from django.db.models import Q, F
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import Article, Author, Comment, ArticleImage
from categories.models import Category
from ads.models import AdUnit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_active_ads(position):
    return AdUnit.objects.filter(position=position, is_active=True).first()


def get_sidebar_ads():
    return {
        'sidebar_top':    get_active_ads(AdUnit.Position.SIDEBAR_TOP),
        'sidebar_sticky': get_active_ads(AdUnit.Position.SIDEBAR_STICKY),
    }


# ---------------------------------------------------------------------------
# Home View
# ---------------------------------------------------------------------------

class HomeView(View):
    template_name = 'home.html'

    def get(self, request):
        published = Article.objects.filter(
            status=Article.Status.PUBLISHED
        ).select_related('author', 'category')

        hero = published.filter(
            priority__in=[
                Article.Priority.EDITOR,
                Article.Priority.FEATURED,
                Article.Priority.BREAKING,
            ]
        ).first() or published.first()

        exclude_pk = hero.pk if hero else 0

        side_articles = published.exclude(pk=exclude_pk)[:4]
        latest        = published.exclude(pk=exclude_pk)[:6]
        editors_pick  = published.filter(priority=Article.Priority.EDITOR).first()

        sport_category    = Category.objects.filter(slug='sport', is_active=True).first()
        sport_articles    = published.filter(category=sport_category)[:3] if sport_category else []

        politics_category = Category.objects.filter(slug='politics', is_active=True).first()
        politics_articles = published.filter(category=politics_category)[:3] if politics_category else []

        context = {
            'hero':               hero,
            'side_articles':      side_articles,
            'latest':             latest,
            'editors_pick':       editors_pick,
            'sport_articles':     sport_articles,
            'politics_articles':  politics_articles,
            # Ads
            'between_cards':      get_active_ads(AdUnit.Position.BETWEEN_CARDS),
            # nav_categories, ticker_items, leaderboard_top come from context processor
        }
        return render(request, self.template_name, context)


# ---------------------------------------------------------------------------
# Article Detail View
# ---------------------------------------------------------------------------

class ArticleDetailView(View):
    template_name = 'detail.html'

    def get(self, request, slug):
        article = get_object_or_404(
            Article.objects.select_related('author', 'category'),
            slug=slug,
            status=Article.Status.PUBLISHED,
        )

        article.increment_views()

        related = Article.objects.filter(
            status=Article.Status.PUBLISHED,
            category=article.category,
        ).exclude(pk=article.pk).select_related('author', 'category').order_by('-published_at')[:4]

        comments = article.comments.filter(
            is_approved=True, parent=None
        ).order_by('created_at')

        gallery     = article.gallery_images.all()
        tags        = article.tags.all()
        sponsorship = getattr(article, 'sponsorship', None)

        context = {
            'article':       article,
            'related':       related,
            'comments':      comments,
            'comment_count': article.comments.filter(is_approved=True).count(),
            'gallery':       gallery,
            'tags':          tags,
            'in_article_1':  get_active_ads(AdUnit.Position.IN_ARTICLE_1),
            'in_article_2':  get_active_ads(AdUnit.Position.IN_ARTICLE_2),
            'sponsorship':   sponsorship,
            **get_sidebar_ads(),
        }
        return render(request, self.template_name, context)


# ---------------------------------------------------------------------------
# Comment Submit
# ---------------------------------------------------------------------------

@require_POST
def submit_comment(request, slug):
    article = get_object_or_404(Article, slug=slug, status=Article.Status.PUBLISHED)

    if not article.allow_comments:
        messages.error(request, "Comments are closed for this article.")
        return redirect(article.get_absolute_url())

    name      = request.POST.get('name', '').strip()
    email     = request.POST.get('email', '').strip()
    body      = request.POST.get('body', '').strip()
    parent_id = request.POST.get('parent_id')

    if not all([name, email, body]):
        messages.error(request, "Please fill in all fields.")
        return redirect(article.get_absolute_url())

    parent = None
    if parent_id:
        try:
            parent = Comment.objects.get(pk=parent_id, article=article)
        except Comment.DoesNotExist:
            pass

    Comment.objects.create(
        article=article,
        parent=parent,
        name=name,
        email=email,
        body=body,
        is_approved=False,
    )

    messages.success(request, "Your comment has been submitted and is awaiting moderation.")
    return redirect(article.get_absolute_url())


# ---------------------------------------------------------------------------
# Category View  — FIXED
# ---------------------------------------------------------------------------

class CategoryView(View):
    template_name = 'category.html'
    paginate_by   = 12

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug, is_active=True)

        # Build category id list — include children only if the FK exists
        category_ids = [category.pk]
        if hasattr(category, 'children'):
            category_ids += list(
                category.children.filter(is_active=True).values_list('pk', flat=True)
            )

        articles = Article.objects.filter(
            status=Article.Status.PUBLISHED,
            category__in=category_ids,
        ).select_related('author', 'category').order_by('-published_at')

        # Debug helper — remove in production
        # print(f"[CategoryView] slug={slug} ids={category_ids} count={articles.count()}")

        paginator = Paginator(articles, self.paginate_by)
        page_obj  = paginator.get_page(request.GET.get('page'))

        featured = articles.filter(
            priority__in=[Article.Priority.FEATURED, Article.Priority.EDITOR]
        ).first() or articles.first()

        sub_cats = category.children.filter(is_active=True) if hasattr(category, 'children') else []

        context = {
            'category':    category,
            'page_obj':    page_obj,
            'featured':    featured,
            'sub_cats':    sub_cats,
            'leaderboard': get_active_ads(AdUnit.Position.LEADERBOARD_TOP),
        }
        return render(request, self.template_name, context)


# ---------------------------------------------------------------------------
# Author Profile View
# ---------------------------------------------------------------------------

class AuthorDetailView(View):
    template_name = 'author.html'
    paginate_by   = 10

    def get(self, request, slug):
        author   = get_object_or_404(Author, slug=slug, is_active=True)
        articles = Article.objects.filter(
            author=author, status=Article.Status.PUBLISHED
        ).select_related('category').order_by('-published_at')

        paginator = Paginator(articles, self.paginate_by)
        page_obj  = paginator.get_page(request.GET.get('page'))

        context = {
            'author':   author,
            'page_obj': page_obj,
            'total':    articles.count(),
        }
        return render(request, self.template_name, context)


# ---------------------------------------------------------------------------
# Search View
# ---------------------------------------------------------------------------

class SearchView(View):
    template_name = 'search.html'
    paginate_by   = 10

    def get(self, request):
        query    = request.GET.get('q', '').strip()
        page_obj = None
        total    = 0

        if query:
            results = Article.objects.filter(
                status=Article.Status.PUBLISHED,
            ).filter(
                Q(title__icontains=query)    |
                Q(excerpt__icontains=query)  |
                Q(body__icontains=query)     |
                Q(tags__name__icontains=query) |
                Q(author__full_name__icontains=query) |
                Q(category__name__icontains=query)
            ).select_related('author', 'category').distinct().order_by('-published_at')

            total     = results.count()
            paginator = Paginator(results, self.paginate_by)
            page_obj  = paginator.get_page(request.GET.get('page'))

        context = {
            'query':    query,
            'page_obj': page_obj,
            'total':    total,
        }
        return render(request, self.template_name, context)


# ---------------------------------------------------------------------------
# Tag View
# ---------------------------------------------------------------------------

class TagView(View):
    template_name = 'tag.html'
    paginate_by   = 12

    def get(self, request, tag_slug):
        articles = Article.objects.filter(
            status=Article.Status.PUBLISHED,
            tags__slug=tag_slug,
        ).select_related('author', 'category').order_by('-published_at')

        if not articles.exists():
            raise Http404

        paginator = Paginator(articles, self.paginate_by)
        page_obj  = paginator.get_page(request.GET.get('page'))

        context = {
            'tag_slug': tag_slug,
            'page_obj': page_obj,
            'total':    articles.count(),
        }
        return render(request, self.template_name, context)


# ---------------------------------------------------------------------------
# Ad Click Tracker
# ---------------------------------------------------------------------------

@require_POST
def track_ad_click(request, ad_id):
    ad = get_object_or_404(AdUnit, pk=ad_id)
    ad.record_click()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------------------
# Latest Articles API
# ---------------------------------------------------------------------------

def latest_articles_api(request):
    articles = Article.objects.filter(
        status=Article.Status.PUBLISHED
    ).select_related('author', 'category').order_by('-published_at')[:10]

    data = [
        {
            'title':        a.title,
            'slug':         a.slug,
            'excerpt':      a.excerpt,
            'category':     a.category.name if a.category else '',
            'author':       a.author.full_name if a.author else '',
            'published':    a.published_at.isoformat() if a.published_at else '',
            'url':          a.get_absolute_url(),
            'image':        a.hero_image.url if a.hero_image else '',
            'reading_time': a.reading_time,
            'priority':     a.priority,
        }
        for a in articles
    ]
    return JsonResponse({'articles': data})