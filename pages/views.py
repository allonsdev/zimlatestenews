from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Page, ContactSubmission, NewsletterSubscriber, TickerItem


# ---------------------------------------------------------------------------
# Static Page View  (About, Privacy, Terms, Advertise…)
# ---------------------------------------------------------------------------

class PageDetailView(View):
    template_name = 'detail.html'

    def get(self, request, slug):
        page = get_object_or_404(Page, slug=slug, status=Page.Status.PUBLISHED)

        # Choose template based on page type
        template_map = {
            Page.Template.CONTACT:   'contact.html',
            Page.Template.ABOUT:     'about.html',
            Page.Template.ADVERTISE: 'advertise.html',
        }
        template = template_map.get(page.template, self.template_name)

        return render(request, template, {'page': page})


# ---------------------------------------------------------------------------
# Contact Form View
# ---------------------------------------------------------------------------

class ContactView(View):
    template_name = 'contact.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name       = request.POST.get('name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        topic      = request.POST.get('topic', ContactSubmission.Topic.GENERAL)
        subject    = request.POST.get('subject', '').strip()
        message    = request.POST.get('message', '').strip()
        attachment = request.FILES.get('attachment')

        # Basic validation
        errors = []
        if not name:    errors.append("Name is required.")
        if not email:   errors.append("Email is required.")
        if not subject: errors.append("Subject is required.")
        if not message: errors.append("Message is required.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, self.template_name, {
                'form_data': request.POST,
            })

        # Save submission
        submission = ContactSubmission.objects.create(
            name=name,
            email=email,
            phone=phone,
            topic=topic,
            subject=subject,
            message=message,
            attachment=attachment,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        # Email notification to editors
        try:
            send_mail(
                subject=f"[{submission.get_topic_display()}] {subject}",
                message=f"From: {name} <{email}>\n\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, "Thank you! Your message has been received. We'll get back to you shortly.")
        return redirect('pages:contact_success')

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class ContactSuccessView(View):
    def get(self, request):
        return render(request, 'contact_success.html')


# ---------------------------------------------------------------------------
# Newsletter Subscribe
# ---------------------------------------------------------------------------

class NewsletterSubscribeView(View):

    def post(self, request):
        email     = request.POST.get('email', '').strip().lower()
        name      = request.POST.get('name', '').strip()
        frequency = request.POST.get('frequency', NewsletterSubscriber.Frequency.DAILY)

        if not email:
            messages.error(request, "Please enter a valid email address.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={
                'name':       name,
                'frequency':  frequency,
                'is_active':  True,
                'ip_address': request.META.get('REMOTE_ADDR'),
            }
        )

        if not created:
            if not subscriber.is_active:
                # Re-subscribe
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.save(update_fields=['is_active', 'unsubscribed_at'])
                messages.success(request, "Welcome back! You've been re-subscribed.")
            else:
                messages.info(request, "You're already subscribed!")
        else:
            # Generate confirm token & send confirmation email
            subscriber.generate_token()
            try:
                confirm_url = request.build_absolute_uri(
                    f"/newsletter/confirm/{subscriber.token}/"
                )
                send_mail(
                    subject="Confirm your ZimLatestNews subscription",
                    message=f"Hi {name or 'there'},\n\nClick to confirm:\n{confirm_url}\n\nIf you didn't subscribe, ignore this email.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "Almost done! Check your email to confirm your subscription.")

        return redirect(request.META.get('HTTP_REFERER', '/'))


class NewsletterConfirmView(View):
    def get(self, request, token):
        subscriber = get_object_or_404(NewsletterSubscriber, token=token)
        subscriber.confirmed = True
        subscriber.save(update_fields=['confirmed'])
        messages.success(request, "Your subscription is confirmed. Welcome to ZimLatestNews!")
        return render(request, 'newsletter_confirmed.html', {'subscriber': subscriber})


class NewsletterUnsubscribeView(View):
    def get(self, request, token):
        subscriber = get_object_or_404(NewsletterSubscriber, token=token)
        return render(request, 'newsletter_unsubscribe.html', {'subscriber': subscriber})

    def post(self, request, token):
        subscriber = get_object_or_404(NewsletterSubscriber, token=token)
        subscriber.is_active        = False
        subscriber.unsubscribed_at  = timezone.now()
        subscriber.save(update_fields=['is_active', 'unsubscribed_at'])
        messages.success(request, "You've been unsubscribed. Sorry to see you go!")
        return render(request, 'newsletter_unsubscribed.html')


# ---------------------------------------------------------------------------
# Custom 404 & 500 handlers  (register in config/urls.py)
# ---------------------------------------------------------------------------

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)