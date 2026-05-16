# articles/urls.py

from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Home
    path('',
         views.HomeView.as_view(),
         name='home'),

    # Article detail
    path('article/<slug:slug>/',
         views.ArticleDetailView.as_view(),
         name='detail'),

    # Submit comment on an article
    path('article/<slug:slug>/comment/',
         views.submit_comment,
         name='submit_comment'),

    # Author profile
    path('author/<slug:slug>/',
         views.AuthorDetailView.as_view(),
         name='author_detail'),

    # Search
    path('search/',
         views.SearchView.as_view(),
         name='search'),

    # Articles by tag
    path('tag/<slug:tag_slug>/',
         views.TagView.as_view(),
         name='tag'),

    # JSON API — latest 10 articles (used by ticker + infinite scroll)
    path('api/latest/',
         views.latest_articles_api,
         name='api_latest'),

    # Ad click tracker (AJAX POST)
    path('ads/click/<int:ad_id>/',
         views.track_ad_click,
         name='track_ad_click'),
]