from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def category_image_path(instance, filename):
    return f"categories/{instance.slug}/{filename}"


class Category(models.Model):

    class Color(models.TextChoices):
        NAVY   = 'navy',   'Navy'
        RED    = 'red',    'Red'
        GREEN  = 'green',  'Green'
        GOLD   = 'gold',   'Gold'
        PURPLE = 'purple', 'Purple'
        TEAL   = 'teal',   'Teal'
        ORANGE = 'orange', 'Orange'
        PINK   = 'pink',   'Pink'

    # Core
    name        = models.CharField(max_length=80, unique=True)
    slug        = models.SlugField(max_length=90, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Short blurb shown on the category landing page")

    # Hierarchy — supports sub-categories (e.g. Sport → Football)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children',
        help_text="Leave blank for top-level categories"
    )

    # Visual identity
    icon        = models.CharField(max_length=60, blank=True, help_text="Tabler icon name, e.g. 'ti-ball-football'")
    color       = models.CharField(max_length=10, choices=Color.choices, default=Color.NAVY)
    cover_image = models.ImageField(upload_to=category_image_path, blank=True, null=True,
                                    help_text="Banner image shown at top of category page")

    # SEO
    seo_title       = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)

    # Navigation
    show_in_nav  = models.BooleanField(default=True, help_text="Show this category in the top navigation bar")
    nav_order    = models.PositiveSmallIntegerField(default=0, help_text="Lower number = further left in nav")
    is_active    = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nav_order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} › {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('categories:detail', kwargs={'slug': self.slug})

    @property
    def article_count(self):
        from articles.models import Article
        return self.articles.filter(status=Article.Status.PUBLISHED).count()

    @property
    def is_top_level(self):
        return self.parent is None

    def get_ancestors(self):
        """Returns list of ancestor categories from root to self."""
        ancestors = []
        node = self.parent
        while node is not None:
            ancestors.insert(0, node)
            node = node.parent
        return ancestors