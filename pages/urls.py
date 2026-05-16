# pages/urls.py

from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Contact form
    path('contact/',
         views.ContactView.as_view(),
         name='contact'),

    # Contact success
    path('contact/success/',
         views.ContactSuccessView.as_view(),
         name='contact_success'),

    # Newsletter subscribe (POST only — form submits here)
    path('newsletter/subscribe/',
         views.NewsletterSubscribeView.as_view(),
         name='newsletter_subscribe'),

    # Confirm subscription via email link
    path('newsletter/confirm/<str:token>/',
         views.NewsletterConfirmView.as_view(),
         name='newsletter_confirm'),

    # Unsubscribe via email link
    path('newsletter/unsubscribe/<str:token>/',
         views.NewsletterUnsubscribeView.as_view(),
         name='newsletter_unsubscribe'),

    # Static pages — MUST be last so it doesn't swallow other routes
    # e.g. /pages/about/  /pages/privacy/  /pages/advertise/
    path('<slug:slug>/',
         views.PageDetailView.as_view(),
         name='detail'),
]