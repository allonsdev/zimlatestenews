from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField


# ---------------------------------------------------------------------------
# Static Page  (About, Contact, Advertise, Privacy, Terms…)
# ---------------------------------------------------------------------------

class Page(models.Model):

    class Status(models.TextChoices):
        DRAFT     = 'draft',     'Draft'
        PUBLISHED = 'published', 'Published'

    class Template(models.TextChoices):
        DEFAULT   = 'default',  'Default (full width)'
        CONTACT   = 'contact',  'Contact Page'
        ABOUT     = 'about',    'About Page'
        ADVERTISE = 'advertise','Advertise Page'

    title    = models.CharField(max_length=200)
    slug     = models.SlugField(max_length=220, unique=True, blank=True)
    body     = RichTextUploadingField()
    status   = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    template = models.CharField(max_length=20, choices=Template.choices, default=Template.DEFAULT,
                                help_text="Choose the layout for this page")

    # SEO
    seo_title       = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)

    # Navigation
    show_in_footer = models.BooleanField(default=True)
    footer_order   = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('pages:detail', kwargs={'slug': self.slug})


# ---------------------------------------------------------------------------
# Contact Form Submission
# ---------------------------------------------------------------------------

class ContactSubmission(models.Model):

    class Topic(models.TextChoices):
        GENERAL    = 'general',    'General Enquiry'
        TIP        = 'tip',        'News Tip'
        ADVERTISE  = 'advertise',  'Advertising'
        CORRECTION = 'correction', 'Correction Request'
        TAKEDOWN   = 'takedown',   'Takedown Request'
        OTHER      = 'other',      'Other'

    name       = models.CharField(max_length=120)
    email      = models.EmailField()
    phone      = models.CharField(max_length=20, blank=True)
    topic      = models.CharField(max_length=15, choices=Topic.choices, default=Topic.GENERAL)
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    attachment = models.FileField(upload_to='contact_attachments/', blank=True, null=True)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_read    = models.BooleanField(default=False)
    is_replied = models.BooleanField(default=False)
    notes      = models.TextField(blank=True, help_text="Internal staff notes")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'

    def __str__(self):
        return f"[{self.get_topic_display()}] {self.name} — {self.subject[:60]}"


# ---------------------------------------------------------------------------
# Newsletter Subscriber
# ---------------------------------------------------------------------------

class NewsletterSubscriber(models.Model):

    class Frequency(models.TextChoices):
        DAILY   = 'daily',   'Daily digest'
        WEEKLY  = 'weekly',  'Weekly roundup'
        BREAKING = 'breaking', 'Breaking news only'

    email       = models.EmailField(unique=True)
    name        = models.CharField(max_length=120, blank=True)
    frequency   = models.CharField(max_length=10, choices=Frequency.choices, default=Frequency.DAILY)
    is_active   = models.BooleanField(default=True)
    confirmed   = models.BooleanField(default=False, help_text="Email confirmed via double opt-in")
    token       = models.CharField(max_length=64, blank=True, help_text="Unsubscribe / confirm token")

    # Interest topics (categories they want to hear about)
    interests   = models.ManyToManyField('categories.Category', blank=True)

    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    subscribed_at   = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'

    def __str__(self):
        status = 'active' if self.is_active else 'unsubscribed'
        return f"{self.email} ({status})"

    def generate_token(self):
        import secrets
        self.token = secrets.token_urlsafe(48)
        self.save(update_fields=['token'])


# ---------------------------------------------------------------------------
# Breaking News Ticker  (the scrolling bar at the top of the site)
# ---------------------------------------------------------------------------

class TickerItem(models.Model):
    text       = models.CharField(max_length=300)
    url        = models.URLField(blank=True, help_text="Optional link — leave blank for text-only")
    is_active  = models.BooleanField(default=True)
    order      = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Ticker Item'
        verbose_name_plural = 'Ticker Items'

    def __str__(self):
        return self.text[:80]

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False