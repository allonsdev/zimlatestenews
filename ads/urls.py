# ads/urls.py

from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    # Record an ad impression (called via JS IntersectionObserver)
    path('impression/<int:ad_id>/',
         views.record_impression,
         name='impression'),

    # Record an ad click (called via JS on direct/house ad clicks)
    path('click/<int:ad_id>/',
         views.record_click,
         name='click'),

    # Return rendered HTML for an ad position (used by AJAX loaders)
    # e.g. /ads/render/sidebar_top/
    path('render/<str:position>/',
         views.render_ad,
         name='render'),
]