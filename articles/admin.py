# articles/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count

from .models import Article, Author, ArticleImage, Comment, RelatedArticle


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------

class ArticleImageInline(admin.TabularInline):
    model       = ArticleImage
    extra       = 1
    fields      = ('image', 'caption', 'credit', 'order')
    ordering    = ('order',)


class RelatedArticleInline(admin.TabularInline):
    model               = RelatedArticle
    fk_name             = 'article'
    extra               = 2
    fields              = ('related', 'order')
    autocomplete_fields = ['related']
    ordering            = ('order',)


class CommentInline(admin.TabularInline):
    model      = Comment
    extra      = 0
    fields     = ('name', 'email', 'body', 'is_approved', 'created_at')
    readonly_fields = ('name', 'email', 'body', 'created_at')
    can_delete = True
    show_change_link = True


# ---------------------------------------------------------------------------
# Author Admin
# ---------------------------------------------------------------------------

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display   = ('photo_thumb', 'full_name', 'title', 'article_count_display', 'is_active')
    list_display_links = ('full_name',)
    list_filter    = ('is_active',)
    search_fields  = ('full_name', 'bio', 'user__email')
    prepopulated_fields = {'slug': ('full_name',)}
    readonly_fields = ('photo_thumb', 'created_at', 'updated_at')

    fieldsets = (
        ('Identity', {
            'fields': ('user', 'full_name', 'slug', 'title', 'bio', 'photo', 'photo_thumb')
        }),
        ('Social Links', {
            'classes': ('collapse',),
            'fields': ('twitter', 'facebook', 'linkedin', 'instagram', 'website')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def photo_thumb(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;">', obj.photo.url)
        return '—'
    photo_thumb.short_description = 'Photo'

    def article_count_display(self, obj):
        return obj.article_count
    article_count_display.short_description = 'Articles'


# ---------------------------------------------------------------------------
# Article Admin
# ---------------------------------------------------------------------------

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display   = (
        'hero_thumb', 'title', 'category', 'author',
        'status_badge', 'priority_badge', 'views',
        'reading_time', 'published_at'
    )
    list_display_links = ('title',)
    list_filter    = ('status', 'priority', 'category', 'is_sponsored', 'is_premium', 'allow_comments', 'show_ads')
    search_fields  = ('title', 'excerpt', 'body', 'author__full_name', 'tags__name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    ordering       = ('-created_at',)
    readonly_fields = (
        'hero_thumb', 'views', 'reading_time',
        'created_at', 'updated_at', 'published_at'
    )
    autocomplete_fields = ['author', 'category']
    filter_horizontal   = ('co_authors',)
    inlines = [ArticleImageInline, RelatedArticleInline, CommentInline]

    fieldsets = (
        ('Content', {
            'fields': (
                'title', 'slug', 'subtitle', 'excerpt', 'body',
            )
        }),
        ('Media', {
            'fields': ('hero_image', 'hero_thumb', 'hero_image_caption', 'hero_image_credit', 'video_url')
        }),
        ('Classification', {
            'fields': ('category', 'author', 'co_authors', 'tags')
        }),
        ('Publishing', {
            'fields': ('status', 'priority', 'scheduled_for', 'published_at')
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description', 'canonical_url')
        }),
        ('Social / Open Graph', {
            'classes': ('collapse',),
            'fields': ('og_image', 'og_title', 'og_description')
        }),
        ('Monetisation & Settings', {
            'classes': ('collapse',),
            'fields': (
                'show_ads', 'is_premium', 'is_sponsored', 'sponsor_name',
                'allow_comments'
            )
        }),
        ('Stats', {
            'classes': ('collapse',),
            'fields': ('views', 'reading_time', 'created_at', 'updated_at')
        }),
    )

    # ---- Custom display columns ----------------------------------------

    def hero_thumb(self, obj):
        if obj.hero_image:
            return format_html(
                '<img src="{}" style="width:80px;height:50px;object-fit:cover;border-radius:4px;">',
                obj.hero_image.url
            )
        return '—'
    hero_thumb.short_description = 'Image'

    def status_badge(self, obj):
        colours = {
            'draft':     '#94a3b8',
            'review':    '#f59e0b',
            'published': '#22c55e',
            'archived':  '#ef4444',
        }
        colour = colours.get(obj.status, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            colour, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def priority_badge(self, obj):
        if obj.priority == 'normal':
            return '—'
        colours = {
            'featured': '#3b82f6',
            'breaking': '#ef4444',
            'editor':   '#8b5cf6',
        }
        colour = colours.get(obj.priority, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            colour, obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    # ---- Bulk actions --------------------------------------------------

    actions = ['publish_articles', 'unpublish_articles', 'mark_featured', 'mark_breaking']

    @admin.action(description='Publish selected articles')
    def publish_articles(self, request, queryset):
        updated = queryset.filter(status__in=['draft', 'review']).update(
            status='published',
            published_at=timezone.now()
        )
        self.message_user(request, f"{updated} article(s) published.")

    @admin.action(description='Unpublish selected articles')
    def unpublish_articles(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f"{updated} article(s) moved back to draft.")

    @admin.action(description='Mark selected as Featured')
    def mark_featured(self, request, queryset):
        queryset.update(priority='featured')
        self.message_user(request, "Selected articles marked as Featured.")

    @admin.action(description='Mark selected as Breaking News')
    def mark_breaking(self, request, queryset):
        queryset.update(priority='breaking')
        self.message_user(request, "Selected articles marked as Breaking News.")


# ---------------------------------------------------------------------------
# Comment Admin
# ---------------------------------------------------------------------------

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'article_link', 'is_approved', 'is_reply', 'created_at')
    list_filter   = ('is_approved',)
    search_fields = ('name', 'email', 'body', 'article__title')
    readonly_fields = ('article', 'parent', 'name', 'email', 'body', 'created_at')
    actions = ['approve_comments', 'reject_comments']

    def article_link(self, obj):
        return format_html('<a href="{}">{}</a>', obj.article.get_absolute_url(), obj.article.title[:50])
    article_link.short_description = 'Article'

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Reject selected comments')
    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)