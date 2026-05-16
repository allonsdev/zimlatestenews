from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

from .models import AdUnit


# ---------------------------------------------------------------------------
# Record Impression  — called via JS fetch() when an ad enters the viewport
# ---------------------------------------------------------------------------

@csrf_exempt
@require_POST
def record_impression(request, ad_id):
    ad = get_object_or_404(AdUnit, pk=ad_id)
    if ad.is_live:
        ad.record_impression()
    return JsonResponse({'status': 'ok'})


# ---------------------------------------------------------------------------
# Record Click  — called via JS fetch() when a direct / house ad is clicked
# ---------------------------------------------------------------------------

@csrf_exempt
@require_POST
def record_click(request, ad_id):
    ad = get_object_or_404(AdUnit, pk=ad_id)
    ad.record_click()
    return JsonResponse({'status': 'ok', 'url': ad.target_url})


# ---------------------------------------------------------------------------
# Render Ad  — returns the HTML for a given position (used by AJAX loaders)
# ---------------------------------------------------------------------------

@require_GET
def render_ad(request, position):
    ad = AdUnit.objects.filter(position=position, is_active=True).first()
    if not ad or not ad.is_live:
        return HttpResponse('')
    return HttpResponse(ad.render())