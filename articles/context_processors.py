# articles/context_processors.py
#
# Add to settings.py TEMPLATES[0]['OPTIONS']['context_processors']:
#   'articles.context_processors.global_context'

from categories.models import Category
from pages.models import TickerItem
from ads.models import AdUnit


def global_context(request):
    """
    Injects into every template:
      - nav_categories   : top-level categories shown in the nav bar
      - ticker_items     : active breaking news ticker items
      - leaderboard_top  : top leaderboard ad unit
    """
    nav_categories = Category.objects.filter(
        show_in_nav=True, is_active=True
    ).order_by('nav_order')

    ticker_items = TickerItem.objects.filter(is_active=True).order_by('order')[:10]

    leaderboard_top = AdUnit.objects.filter(
        position=AdUnit.Position.LEADERBOARD_TOP, is_active=True
    ).first()

    return {
        'nav_categories':  nav_categories,
        'ticker_items':    ticker_items,
        'leaderboard_top': leaderboard_top,
    }
