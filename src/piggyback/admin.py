from django.contrib import admin
from django.utils.html import format_html

from piggyback.models import (
    BillingProfile,
    Card,
    CardLibraryEntry,
    CardTemplate,
    Delivery,
    DesignAsset,
    GiftAddon,
    Occasion,
    OccasionCategory,
    Order,
    OrderItem,
    Recipient,
    Reminder,
    Subscription,
    SubscriptionPlan,
)


@admin.register(OccasionCategory)
class OccasionCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "icon", "is_featured", "sort_order"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["is_featured", "sort_order"]


@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_seasonal"]
    list_filter = ["category", "is_seasonal"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CardTemplate)
class CardTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "occasion", "style", "is_premium", "is_active", "popularity_score"]
    list_filter = ["style", "is_premium", "is_active", "occasion__category"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]


@admin.register(DesignAsset)
class DesignAssetAdmin(admin.ModelAdmin):
    list_display = ["name", "asset_type", "is_premium"]
    list_filter = ["asset_type", "is_premium"]


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "status", "is_favorite", "updated_at"]
    list_filter = ["status", "is_favorite"]
    search_fields = ["title", "owner__username"]
    readonly_fields = ["preview_thumb"]

    @admin.display(description="Preview")
    def preview_thumb(self, obj):
        if obj.preview_image:
            return format_html('<img src="{}" width="120" />', obj.preview_image.url)
        return "—"


@admin.register(CardLibraryEntry)
class CardLibraryEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "card", "entry_type", "is_pinned"]
    list_filter = ["entry_type", "is_pinned"]


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ["full_name", "owner", "email", "city", "birthday", "is_system_user"]
    list_filter = ["country", "is_system_user"]
    search_fields = ["first_name", "last_name", "email"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["uuid", "user", "status", "total_pence", "payment_provider", "created_at"]
    list_filter = ["status"]
    inlines = [OrderItemInline]
    readonly_fields = ["uuid", "paid_at"]


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ["id", "order_item", "status", "scheduled_for", "tracking_reference"]
    list_filter = ["status"]
    readonly_fields = ["view_token"]


@admin.register(GiftAddon)
class GiftAddonAdmin(admin.ModelAdmin):
    list_display = ["name", "price_pence", "is_active"]


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ["title", "user", "event_date", "days_before", "is_active"]
    list_filter = ["reminder_type", "is_active"]


@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "billing_email", "stripe_customer_id", "updated_at"]
    search_fields = ["user__username", "billing_email", "stripe_customer_id"]


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "amount_pence",
        "interval",
        "is_active",
        "grants_premium_access",
    ]
    list_filter = ["interval", "is_active", "grants_premium_access"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "slug", "stripe_price_id"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "current_period_end", "cancel_at_period_end"]
    list_filter = ["status", "plan", "cancel_at_period_end"]
    search_fields = ["user__username", "stripe_subscription_id", "stripe_customer_id"]
    readonly_fields = ["stripe_subscription_id"]
