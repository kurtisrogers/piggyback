from django.contrib import admin
from django.urls import include, path

from piggyback.views import web

app_name = "piggyback"

urlpatterns = [
    path("", web.HomeView.as_view(), name="home"),
    path("catalog/", web.CatalogView.as_view(), name="catalog"),
    path("editor/", web.EditorView.as_view(), name="editor_new"),
    path("editor/<int:card_id>/", web.EditorView.as_view(), name="editor"),
    path("editor/template/<slug:template_slug>/", web.EditorView.as_view(), name="editor_template"),
    path("library/", web.LibraryView.as_view(), name="library"),
    path("recipients/", web.RecipientsView.as_view(), name="recipients"),
    path("cart/", web.CartView.as_view(), name="cart"),
    path("checkout/<uuid:uuid>/", web.CheckoutView.as_view(), name="checkout"),
    path("orders/<uuid:uuid>/", web.OrderConfirmationView.as_view(), name="order_confirmation"),
    path("cards/view/<uuid:token>/", web.CardViewView.as_view(), name="card_view"),
    path("reminders/", web.RemindersView.as_view(), name="reminders"),
    path("api/", include("piggyback.api.urls")),
]

admin_urls = [
    path("admin/", admin.site.urls),
]
