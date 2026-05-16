# pages/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Page, ContactSubmission, NewsletterSubscriber, TickerItem


# ---------------------------------------------------------------------------
# Page Admin
# ---------------------------------------------------------------------------

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display  = ('title', 'slug', 'template', 'status', 'show_in_footer', 'footer_order', 'updated_at')
    list_filter   = ('status', 'template', 'show_in_footer')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'body')
        }),
        ('Settings', {
            'fields': ('status', 'template', 'show_in_footer', 'footer_order')
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description')
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at')
        }),
    )


# ---------------------------------------------------------------------------
# Contact Submission Admin
# ---------------------------------------------------------------------------

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'topic_badge', 'subject_short', 'is_read', 'is_replied', 'created_at')
    list_filter   = ('topic', 'is_read', 'is_replied')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = (
        'name', 'email', 'phone', 'topic', 'subject',
        'message', 'attachment', 'ip_address', 'user_agent', 'created_at'
    )
    ordering = ('-created_at',)

    fieldsets = (
        ('From', {
            'fields': ('name', 'email', 'phone', 'ip_address', 'user_agent')
        }),
        ('Message', {
            'fields': ('topic', 'subject', 'message', 'attachment')
        }),
        ('Staff', {
            'fields': ('is_read', 'is_replied', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    actions = ['mark_as_read', 'mark_as_replied']

    def topic_badge(self, obj):
        colours = {
            'tip':        '#3b82f6',
            'advertise':  '#f59e0b',
            'correction': '#ef4444',
            'takedown':   '#ef4444',
            'general':    '#94a3b8',
            'other':      '#94a3b8',
        }
        colour = colours.get(obj.topic, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:12px;font-size:11px;">{}</span>',
            colour, obj.get_topic_display()
        )
    topic_badge.short_description = 'Topic'

    def subject_short(self, obj):
        return obj.subject[:60]
    subject_short.short_description = 'Subject'

    @admin.action(description='Mark selected as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='Mark selected as replied')
    def mark_as_replied(self, request, queryset):
        queryset.update(is_replied=True, is_read=True)


# ---------------------------------------------------------------------------
# Newsletter Subscriber Admin
# ---------------------------------------------------------------------------

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display  = ('email', 'name', 'frequency', 'confirmed', 'is_active', 'subscribed_at')
    list_filter   = ('is_active', 'confirmed', 'frequency')
    search_fields = ('email', 'name')
    readonly_fields = ('token', 'ip_address', 'subscribed_at', 'unsubscribed_at')
    filter_horizontal = ('interests',)
    ordering = ('-subscribed_at',)
    actions  = ['activate_subscribers', 'deactivate_subscribers']

    fieldsets = (
        ('Subscriber', {
            'fields': ('email', 'name', 'frequency', 'interests')
        }),
        ('Status', {
            'fields': ('is_active', 'confirmed', 'token')
        }),
        ('Meta', {
            'classes': ('collapse',),
            'fields': ('ip_address', 'subscribed_at', 'unsubscribed_at')
        }),
    )

    @admin.action(description='Activate selected subscribers')
    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected subscribers')
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False, unsubscribed_at=timezone.now())


# ---------------------------------------------------------------------------
# Ticker Item Admin
# ---------------------------------------------------------------------------

@admin.register(TickerItem)
class TickerItemAdmin(admin.ModelAdmin):
    list_display  = ('text_short', 'url', 'is_active', 'order', 'expires_at', 'created_at')
    list_filter   = ('is_active',)
    search_fields = ('text',)
    ordering      = ('order', '-created_at')

    fieldsets = (
        ('Content', {
            'fields': ('text', 'url')
        }),
        ('Settings', {
            'fields': ('is_active', 'order', 'expires_at')
        }),
    )

    def text_short(self, obj):
        return obj.text[:80]
    text_short.short_description = 'Text'