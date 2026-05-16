from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def article_image_path(instance, filename):
    now = timezone.now()
    return f"articles/{now.year}/{now.month:02d}/{filename}"


def author_photo_path(instance, filename):
    return f"authors/{filename}"


# ---------------------------------------------------------------------------
# Author
# ---------------------------------------------------------------------------

class Author(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    full_name  = models.CharField()
    slug       = models.SlugField(unique=True, blank=True)
    bio        = models.TextField(blank=True)
    photo      = models.ImageField(upload_to=author_photo_path, blank=True, null=True)
    title      = models.CharField(blank=True, help_text="e.g. Senior Reporter, Editor")

    # Social links
    twitter    = models.URLField(blank=True)
    facebook   = models.URLField(blank=True)
    linkedin   = models.URLField(blank=True)
    instagram  = models.URLField(blank=True)
    website    = models.URLField(blank=True)

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articles:author_detail', kwargs={'slug': self.slug})

    @property
    def article_count(self):
        return self.articles.filter(status=Article.Status.PUBLISHED).count()


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------

class Article(models.Model):

    class Status(models.TextChoices):
        DRAFT     = 'draft',     'Draft'
        REVIEW    = 'review',    'Under Review'
        PUBLISHED = 'published', 'Published'
        ARCHIVED  = 'archived',  'Archived'

    class Priority(models.TextChoices):
        NORMAL   = 'normal',   'Normal'
        FEATURED = 'featured', 'Featured'
        BREAKING = 'breaking', 'Breaking News'
        EDITOR   = 'editor',   "Editor's Pick"

    # Core fields
    title          = models.CharField()
    slug           = models.SlugField(max_length=255, unique=True, blank=True)
    subtitle       = models.CharField(blank=True, help_text="Appears under the headline")
    excerpt        = models.TextField(help_text="Short summary shown in cards and meta description")
    body           = RichTextUploadingField()

    # Relationships
    author         = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='articles')
    co_authors     = models.ManyToManyField(Author, blank=True, related_name='co_authored_articles')
    category       = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True, related_name='articles')
    tags           = TaggableManager(blank=True)

    # Media
    hero_image         = models.ImageField(upload_to=article_image_path)
    hero_image_caption = models.CharField(blank=True)
    hero_image_credit  = models.CharField(blank=True, help_text="Photographer or agency credit")
    video_url          = models.URLField(blank=True, help_text="Optional YouTube or Vimeo embed URL")

    # Status and priority
    status   = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT, db_index=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL, db_index=True)

    # Dates
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    published_at  = models.DateTimeField(null=True, blank=True, db_index=True)
    scheduled_for = models.DateTimeField(null=True, blank=True, help_text="Auto-publish at this time")

    # SEO
    seo_title       = models.CharField(blank=True, help_text="Overrides title in browser tab and Google")
    seo_description = models.CharField(blank=True, help_text="Overrides excerpt in Google snippet")
    canonical_url   = models.URLField(blank=True, help_text="Set if this article was originally published elsewhere")

    # Open Graph
    og_image       = models.ImageField(upload_to='og/', blank=True, null=True, help_text="1200x630px image for social sharing")
    og_title       = models.CharField(blank=True)
    og_description = models.CharField(blank=True)

    # Engagement
    views        = models.PositiveIntegerField(default=0, editable=False)
    reading_time = models.PositiveSmallIntegerField(default=0, editable=False, help_text="Auto-calculated in minutes")

    # Flags
    is_sponsored   = models.BooleanField(default=False)
    sponsor_name   = models.CharField(blank=True)
    allow_comments = models.BooleanField(default=True)
    show_ads       = models.BooleanField(default=True, help_text="Uncheck to suppress AdSense on this article")
    is_premium     = models.BooleanField(default=False, help_text="Paywall or subscriber only content")

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        indexes = [
            models.Index(fields=['-published_at', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['priority', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        import re
        plain = re.sub(r'<[^>]+>', '', self.body)
        word_count = len(plain.split())
        self.reading_time = max(1, round(word_count / 200))

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})

    def increment_views(self):
        Article.objects.filter(pk=self.pk).update(views=models.F('views') + 1)

    @property
    def display_title(self):
        return self.seo_title or self.title

    @property
    def display_description(self):
        return self.seo_description or self.excerpt

    @property
    def is_breaking(self):
        return self.priority == self.Priority.BREAKING

    @property
    def is_featured(self):
        return self.priority in (self.Priority.FEATURED, self.Priority.BREAKING, self.Priority.EDITOR)


# ---------------------------------------------------------------------------
# Article Images
# ---------------------------------------------------------------------------

class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='gallery_images')
    image   = models.ImageField(upload_to=article_image_path)
    caption = models.CharField(blank=True)
    credit  = models.CharField(blank=True)
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Article Image'
        verbose_name_plural = 'Article Images'

    def __str__(self):
        return f"Image {self.order} — {self.article.title[:50]}"


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

class Comment(models.Model):
    article     = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    parent      = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    name        = models.CharField()
    email       = models.EmailField()
    body        = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"{self.name} on '{self.article.title[:40]}'"

    @property
    def is_reply(self):
        return self.parent is not None


# ---------------------------------------------------------------------------
# Related Articles
# ---------------------------------------------------------------------------

class RelatedArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='related_articles')
    related = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='+')
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('article', 'related')
        verbose_name = 'Related Article'

    def __str__(self):
        return f"{self.article.title[:40]} → {self.related.title[:40]}"