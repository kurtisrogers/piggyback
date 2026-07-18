"""Stripe webhook endpoint (CSRF-exempt)."""

from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from piggyback.services.payments import get_payment_backend


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request):
        signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        backend = get_payment_backend()
        try:
            backend.handle_webhook(request.body, signature)
        except ValueError as exc:
            return HttpResponseBadRequest(str(exc))
        except Exception:
            return HttpResponseBadRequest("Webhook processing failed.")
        return HttpResponse(status=200)
