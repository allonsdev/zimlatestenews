# categories/urls.py

from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    # All categories overview
    path('',
         views.CategoryListView.as_view(),
         name='list'),

    # Single category landing page  e.g. /categories/sport/
    path('<slug:slug>/',
         views.CategoryDetailView.as_view(),
         name='detail'),
]