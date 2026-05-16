from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# Ad Unit  — one entry per AdSense slot / custom banner
# ---------------------------------------------------------------------------

class AdUnit(models.Model):

    class AdType(models.TextChoices):
        ADSENSE        = 'adsense',         'Google AdSense'
        DIRECT_IMAGE   = 'direct_image',    'Direct — Image Banner'
        DIRECT_HTML    = 'direct_html',     'Direct — Custom HTML'
        HOUSE          = 'house',           'House / Promo Ad'

    class Position(models.TextChoices):
        LEADERBOARD_TOP    = 'leaderboard_top',    'Leaderboard — Top of page'
        LEADERBOARD_BOTTOM = 'leaderboard_bottom', 'Leaderboard — Bottom of page'
        IN_ARTICLE_1       = 'in_article_1',       'In-Article — After paragraph 3'
        IN_ARTICLE_2       = 'in_article_2',       'In-Article — After paragraph 6'
        SIDEBAR_TOP        = 'sidebar_top',        'Sidebar — Top'
        SIDEBAR_STICKY     = 'sidebar_sticky',     'Sidebar — Sticky'
        BETWEEN_CARDS      = 'between_cards',      'Between article cards'
        FOOTER             = 'footer',             'Footer banner'

    class Size(models.TextChoices):
        LEADERBOARD   = '728x90',   'Leaderboard (728×90)'
        MEDIUM_RECT   = '300x250',  'Medium Rectangle (300×250)'
        LARGE_RECT    = '336x280',  'Large Rectangle (336×280)'
        HALF_PAGE     = '300x600',  'Half Page (300×600)'
        MOBILE_BANNER = '320x50',   'Mobile Banner (320×50)'
        RESPONSIVE    = 'resp',     'Responsive (auto-size)'

    # Identity
    name     = models.CharField(max_length=120, help_text="Internal label e.g. 'Article sidebar 300x250'")
    ad_type  = models.CharField(max_length=20, choices=AdType.choices, default=AdType.ADSENSE)
    position = models.CharField(max_length=30, choices=Position.choices)
    size     = models.CharField(max_length=10, choices=Size.choices, default=Size.RESPONSIVE)

    # Google AdSense fields
    adsense_publisher_id = models.CharField(
        max_length=30, blank=True,
        help_text="Your ca-pub-XXXXXXXXXXXXXXXX publisher ID"
    )
    adsense_slot_id = models.CharField(
        max_length=20, blank=True,
        help_text="The data-ad-slot value from your AdSense account"
    )

    # Direct / custom ad fields
    image        = models.ImageField(upload_to='ads/', blank=True, null=True)
    target_url   = models.URLField(blank=True, help_text="Where the ad clicks through to")
    custom_html  = models.TextField(blank=True, help_text="Paste any third-party ad code here")
    alt_text     = models.CharField(max_length=150, blank=True, help_text="Alt text for image ads")

    # Scheduling & targeting
    is_active  = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date   = models.DateTimeField(null=True, blank=True)

    # Targeting — show only on these categories (empty = show everywhere)
    categories = models.ManyToManyField(
        'categories.Category', blank=True,
        help_text="Restrict this ad to specific categories. Leave blank to show site-wide."
    )

    # Advertiser info (for direct deals)
    advertiser_name  = models.CharField(max_length=120, blank=True)
    advertiser_email = models.EmailField(blank=True)
    campaign_name    = models.CharField(max_length=150, blank=True)
    notes            = models.TextField(blank=True, help_text="Internal campaign notes")

    # Impression / click tracking (basic)
    impressions = models.PositiveIntegerField(default=0, editable=False)
    clicks      = models.PositiveIntegerField(default=0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'name']
        verbose_name = 'Ad Unit'
        verbose_name_plural = 'Ad Units'

    def __str__(self):
        return f"{self.name} [{self.get_position_display()}]"

    @property
    def is_live(self):
        """Returns True if the ad should currently be displayed."""
        if not self.is_active:
            return False
        now = timezone.now()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True

    @property
    def ctr(self):
        """Click-through rate as a percentage."""
        if self.impressions == 0:
            return 0.0
        return round((self.clicks / self.impressions) * 100, 2)

    def record_impression(self):
        AdUnit.objects.filter(pk=self.pk).update(impressions=models.F('impressions') + 1)

    def record_click(self):
        AdUnit.objects.filter(pk=self.pk).update(clicks=models.F('clicks') + 1)

    def render(self):
        """Returns the HTML snippet to embed in templates."""
        if self.ad_type == self.AdType.ADSENSE:
            w, h = ('auto', 'auto') if self.size == 'resp' else self.size.split('x')
            return (
                f'<ins class="adsbygoogle"'
                f' style="display:block;width:{w}px;height:{h}px;"'
                f' data-ad-client="{self.adsense_publisher_id}"'
                f' data-ad-slot="{self.adsense_slot_id}"'
                f' data-ad-format="{"auto" if self.size == "resp" else "fixed"}"'
                f' data-full-width-responsive="true"></ins>'
                f'<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>'
            )
        if self.ad_type == self.AdType.DIRECT_IMAGE and self.image:
            return (
                f'<a href="{self.target_url}" target="_blank" rel="noopener sponsored">'
                f'<img src="{self.image.url}" alt="{self.alt_text}" '
                f'width="{self.size.split("x")[0] if "x" in self.size else ""}" loading="lazy"></a>'
            )
        if self.ad_type in (self.AdType.DIRECT_HTML, self.AdType.HOUSE):
            return self.custom_html
        return ''


# ---------------------------------------------------------------------------
# Sponsored Post  — full native/sponsored article wrapper
# ---------------------------------------------------------------------------

class SponsoredPost(models.Model):

    class Status(models.TextChoices):
        PENDING  = 'pending',  'Pending Approval'
        ACTIVE   = 'active',   'Active'
        EXPIRED  = 'expired',  'Expired'
        REJECTED = 'rejected', 'Rejected'

    article          = models.OneToOneField(
        'articles.Article', on_delete=models.CASCADE, related_name='sponsorship'
    )
    advertiser_name  = models.CharField(max_length=120)
    advertiser_email = models.EmailField()
    advertiser_logo  = models.ImageField(upload_to='sponsors/', blank=True, null=True)
    advertiser_url   = models.URLField(blank=True)

    disclosure_text = models.CharField(
        max_length=200,
        default='This article is sponsored content.',
        help_text="Disclosure shown above the article body (required by law)"
    )

    status     = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    start_date = models.DateField()
    end_date   = models.DateField()
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2, help_text="Agreed fee in USD")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Sponsored Post'
        verbose_name_plural = 'Sponsored Posts'

    def __str__(self):
        return f"Sponsored: {self.article.title[:60]} — {self.advertiser_name}"

    @property
    def is_live(self):
        from django.utils.timezone import now
        today = now().date()
        return self.status == self.Status.ACTIVE and self.start_date <= today <= self.end_date