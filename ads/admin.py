# ads/admin.py

from django.contrib import admin
from django.utils.html import format_html

from .models import AdUnit, SponsoredPost


# ---------------------------------------------------------------------------
# AdUnit Admin
# ---------------------------------------------------------------------------

@admin.register(AdUnit)
class AdUnitAdmin(admin.ModelAdmin):
    list_display  = (
        'name', 'ad_type_badge', 'position', 'size',
        'is_active', 'is_live_display',
        'impressions', 'clicks', 'ctr_display',
        'start_date', 'end_date'
    )
    list_filter   = ('ad_type', 'position', 'size', 'is_active')
    search_fields = ('name', 'advertiser_name', 'campaign_name', 'adsense_slot_id')
    readonly_fields = ('impressions', 'clicks', 'ctr_display', 'ad_preview', 'created_at', 'updated_at')
    filter_horizontal = ('categories',)
    ordering = ('position', 'name')

    fieldsets = (
        ('Identity', {
            'fields': ('name', 'ad_type', 'position', 'size')
        }),
        ('Google AdSense', {
            'classes': ('collapse',),
            'description': 'Fill these in for AdSense ad units only.',
            'fields': ('adsense_publisher_id', 'adsense_slot_id')
        }),
        ('Direct / Custom Ad', {
            'classes': ('collapse',),
            'description': 'Fill these in for direct image or custom HTML ads.',
            'fields': ('image', 'target_url', 'alt_text', 'custom_html')
        }),
        ('Preview', {
            'fields': ('ad_preview',)
        }),
        ('Scheduling & Targeting', {
            'fields': ('is_active', 'start_date', 'end_date', 'categories')
        }),
        ('Advertiser (direct deals)', {
            'classes': ('collapse',),
            'fields': ('advertiser_name', 'advertiser_email', 'campaign_name', 'notes')
        }),
        ('Performance', {
            'classes': ('collapse',),
            'fields': ('impressions', 'clicks', 'ctr_display', 'created_at', 'updated_at')
        }),
    )

    def ad_type_badge(self, obj):
        colours = {
            'adsense':      '#4285f4',
            'direct_image': '#22c55e',
            'direct_html':  '#f59e0b',
            'house':        '#8b5cf6',
        }
        colour = colours.get(obj.ad_type, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            colour, obj.get_ad_type_display()
        )
    ad_type_badge.short_description = 'Type'

    def is_live_display(self, obj):
        if obj.is_live:
            return format_html('<span style="color:#22c55e;font-weight:600;">● Live</span>')
        return format_html('<span style="color:#ef4444;">● Off</span>')
    is_live_display.short_description = 'Live?'

    def ctr_display(self, obj):
        return f"{obj.ctr}%"
    ctr_display.short_description = 'CTR'

    def ad_preview(self, obj):
        html = obj.render()
        if html:
            return format_html(
                '<div style="border:1px dashed #e2e8f0;padding:12px;border-radius:6px;">{}</div>',
                html
            )
        return 'Save the ad unit first to see a preview.'
    ad_preview.short_description = 'Preview'

    actions = ['activate_ads', 'deactivate_ads']

    @admin.action(description='Activate selected ad units')
    def activate_ads(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected ad units')
    def deactivate_ads(self, request, queryset):
        queryset.update(is_active=False)


# ---------------------------------------------------------------------------
# SponsoredPost Admin
# ---------------------------------------------------------------------------

@admin.register(SponsoredPost)
class SponsoredPostAdmin(admin.ModelAdmin):
    list_display   = (
        'article_title', 'advertiser_name', 'status_badge',
        'amount_usd', 'start_date', 'end_date', 'is_live_display'
    )
    list_filter    = ('status',)
    search_fields  = ('advertiser_name', 'advertiser_email', 'article__title')
    readonly_fields = ('is_live_display', 'created_at')
    autocomplete_fields = ['article']

    fieldsets = (
        ('Article', {
            'fields': ('article',)
        }),
        ('Advertiser', {
            'fields': ('advertiser_name', 'advertiser_email', 'advertiser_logo', 'advertiser_url')
        }),
        ('Campaign', {
            'fields': ('disclosure_text', 'status', 'start_date', 'end_date', 'amount_usd')
        }),
        ('Meta', {
            'classes': ('collapse',),
            'fields': ('is_live_display', 'created_at')
        }),
    )

    def article_title(self, obj):
        return obj.article.title[:60]
    article_title.short_description = 'Article'

    def status_badge(self, obj):
        colours = {
            'pending':  '#f59e0b',
            'active':   '#22c55e',
            'expired':  '#94a3b8',
            'rejected': '#ef4444',
        }
        colour = colours.get(obj.status, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            colour, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def is_live_display(self, obj):
        if obj.is_live:
            return format_html('<span style="color:#22c55e;font-weight:600;">● Live now</span>')
        return format_html('<span style="color:#94a3b8;">● Not live</span>')
    is_live_display.short_description = 'Live?'