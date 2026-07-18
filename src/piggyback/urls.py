from django.contrib import admin
from django.urls import include, path

from piggyback.views import web
from piggyback.views.stripe_webhook import StripeWebhookView

app_name = "piggyback"

urlpatterns = [
    path("", web.HomeView.as_view(), name="home"),
    path("catalog/", web.CatalogView.as_view(), name="catalog"),
    path("editor/", web.EditorView.as_view(), name="editor_new"),
    path("editor/<int:card_id>/", web.EditorView.as_view(), name="editor"),
    path("editor/template/<slug:template_slug>/", web.EditorView.as_view(), name="editor_template"),
    path(
        "editor/<int:card_id>/send/",
        web.EditorSendView.as_view(),
        name="editor_send",
    ),
    path(
        "editor/<int:card_id>/send/modal/",
        web.EditorSendModalView.as_view(),
        name="editor_send_modal",
    ),
    path("library/", web.LibraryView.as_view(), name="library"),
    path(
        "library/favorite/<int:card_id>/",
        web.LibraryFavoriteView.as_view(),
        name="library_favorite",
    ),
    path("recipients/", web.RecipientsView.as_view(), name="recipients"),
    path("recipients/add/", web.RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipients/<int:pk>/delete/",
        web.RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    path("reminders/", web.RemindersView.as_view(), name="reminders"),
    path("reminders/add/", web.ReminderCreateView.as_view(), name="reminder_create"),
    path(
        "reminders/<int:pk>/delete/",
        web.ReminderDeleteView.as_view(),
        name="reminder_delete",
    ),
    path("cart/", web.CartView.as_view(), name="cart"),
    path(
        "cart/remove/<int:item_id>/",
        web.CartRemoveView.as_view(),
        name="cart_remove",
    ),
    path("checkout/<uuid:uuid>/", web.CheckoutView.as_view(), name="checkout"),
    path("subscriptions/", web.SubscriptionPlansView.as_view(), name="subscriptions"),
    path(
        "subscriptions/<slug:slug>/checkout/",
        web.SubscriptionCheckoutView.as_view(),
        name="subscription_checkout",
    ),
    path(
        "subscriptions/portal/",
        web.SubscriptionPortalView.as_view(),
        name="subscription_portal",
    ),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe_webhook"),
    path("orders/<uuid:uuid>/", web.OrderConfirmationView.as_view(), name="order_confirmation"),
    path("cards/view/<uuid:token>/", web.CardViewView.as_view(), name="card_view"),
    path("api/", include("piggyback.api.urls")),
]

admin_urls = [
    path("admin/", admin.site.urls),
]
