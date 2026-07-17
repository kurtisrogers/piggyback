from django.urls import include, path
from rest_framework.routers import DefaultRouter

from piggyback.api import views

router = DefaultRouter()
router.register(r"categories", views.OccasionCategoryViewSet, basename="category")
router.register(r"occasions", views.OccasionViewSet, basename="occasion")
router.register(r"templates", views.CardTemplateViewSet, basename="template")
router.register(r"assets", views.DesignAssetViewSet, basename="asset")
router.register(r"cards", views.CardViewSet, basename="card")
router.register(r"library", views.CardLibraryViewSet, basename="library")
router.register(r"me", views.MeViewSet, basename="me")
router.register(r"recipients", views.RecipientViewSet, basename="recipient")
router.register(r"gifts", views.GiftAddonViewSet, basename="gift")
router.register(r"orders", views.OrderViewSet, basename="order")
router.register(r"deliveries", views.DeliveryViewSet, basename="delivery")
router.register(r"reminders", views.ReminderViewSet, basename="reminder")

urlpatterns = [
    path("", include(router.urls)),
]
