# articles/context_processors.py
# Add this file to your articles app, then register it in settings.py

from categories.models import Category
from ads.models import AdUnit


def global_context(request):
    """
    Injects variables needed on every page:
      - nav_categories  → header/footer nav links
      - ticker_items    → breaking news ticker
      - leaderboard_top → top-of-page ad (base.html)
    """
    # Nav categories
    nav_categories = Category.objects.filter(
        show_in_nav=True, is_active=True
    ).order_by('nav_order')

    # Ticker items — import here to avoid circular imports
    try:
        from pages.models import TickerItem
        ticker_items = TickerItem.objects.filter(is_active=True).order_by('order')
    except Exception:
        ticker_items = []

    # Leaderboard ad
    try:
        leaderboard_top = AdUnit.objects.filter(
            position=AdUnit.Position.LEADERBOARD_TOP, is_active=True
        ).first()
    except Exception:
        leaderboard_top = None

    return {
        'nav_categories':  nav_categories,
        'ticker_items':    ticker_items,
        'leaderboard_top': leaderboard_top,
    }