# categories/admin.py

from django.contrib import admin
from django.utils.html import format_html

from .models import Category


class SubCategoryInline(admin.TabularInline):
    model       = Category
    fk_name     = 'parent'
    extra       = 1
    fields      = ('name', 'slug', 'color', 'icon', 'show_in_nav', 'nav_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display   = (
        'cover_thumb', 'name', 'parent', 'color_badge',
        'article_count_display', 'show_in_nav', 'nav_order', 'is_active'
    )
    list_display_links = ('name',)
    list_filter    = ('is_active', 'show_in_nav', 'color', 'parent')
    search_fields  = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering       = ('nav_order', 'name')
    readonly_fields = ('cover_thumb', 'created_at', 'updated_at', 'article_count_display')
    inlines        = [SubCategoryInline]

    fieldsets = (
        ('Identity', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Visual', {
            'fields': ('cover_image', 'cover_thumb', 'icon', 'color')
        }),
        ('Navigation', {
            'fields': ('show_in_nav', 'nav_order', 'is_active')
        }),
        ('SEO', {
            'classes': ('collapse',),
            'fields': ('seo_title', 'seo_description')
        }),
        ('Stats', {
            'classes': ('collapse',),
            'fields': ('article_count_display', 'created_at', 'updated_at')
        }),
    )

    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width:60px;height:40px;object-fit:cover;border-radius:4px;">',
                obj.cover_image.url
            )
        return '—'
    cover_thumb.short_description = 'Cover'

    def color_badge(self, obj):
        colour_map = {
            'navy': '#0e1f3d', 'red': '#ef4444', 'green': '#22c55e',
            'gold': '#c9a84c', 'purple': '#8b5cf6', 'teal': '#14b8a6',
            'orange': '#f97316', 'pink': '#ec4899',
        }
        hex_col = colour_map.get(obj.color, '#94a3b8')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;">{}</span>',
            hex_col, obj.get_color_display()
        )
    color_badge.short_description = 'Colour'

    def article_count_display(self, obj):
        return obj.article_count
    article_count_display.short_description = 'Articles'