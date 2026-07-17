from rest_framework import serializers

from piggyback.models import (
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
)


class OccasionCategorySerializer(serializers.ModelSerializer):
    occasion_count = serializers.SerializerMethodField()

    class Meta:
        model = OccasionCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "color",
            "is_featured",
            "occasion_count",
        ]

    def get_occasion_count(self, obj):
        return obj.occasions.count()


class OccasionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Occasion
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "category",
            "category_name",
            "is_seasonal",
            "month",
            "day",
        ]


class CardTemplateSerializer(serializers.ModelSerializer):
    occasion_name = serializers.CharField(source="occasion.name", read_only=True, allow_null=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = CardTemplate
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "occasion",
            "occasion_name",
            "style",
            "thumbnail_url",
            "is_premium",
            "popularity_score",
            "canvas_data",
        ]

    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None


class DesignAssetSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = DesignAsset
        fields = ["id", "name", "asset_type", "image_url", "tags", "is_premium"]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CardSerializer(serializers.ModelSerializer):
    preview_url = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = [
            "id",
            "title",
            "status",
            "template",
            "occasion",
            "canvas_data",
            "inside_message",
            "preview_url",
            "is_favorite",
            "sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["sent_at", "created_at", "updated_at"]

    def get_preview_url(self, obj):
        if obj.preview_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.preview_image.url)
            return obj.preview_image.url
        return None

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class CardLibraryEntrySerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)

    class Meta:
        model = CardLibraryEntry
        fields = ["id", "card", "entry_type", "notes", "is_pinned", "created_at"]


class RecipientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Recipient
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "address_line_1",
            "address_line_2",
            "city",
            "county",
            "postcode",
            "country",
            "birthday",
            "anniversary",
            "notes",
        ]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class GiftAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftAddon
        fields = ["id", "name", "description", "price_pence", "image"]


class OrderItemSerializer(serializers.ModelSerializer):
    card_title = serializers.CharField(source="card.title", read_only=True)
    recipient_name = serializers.CharField(
        source="recipient.full_name", read_only=True, allow_null=True
    )
    line_total_pence = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "card",
            "card_title",
            "recipient",
            "recipient_name",
            "delivery_method",
            "gift_addon",
            "gift_wrap",
            "unit_price_pence",
            "quantity",
            "line_total_pence",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "uuid",
            "status",
            "items",
            "subtotal_pence",
            "discount_pence",
            "total_pence",
            "currency",
            "promo_code",
            "created_at",
        ]
        read_only_fields = ["uuid", "status", "subtotal_pence", "discount_pence", "total_pence"]


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = [
            "id",
            "status",
            "scheduled_for",
            "sent_at",
            "delivered_at",
            "tracking_reference",
            "view_token",
        ]
        read_only_fields = fields


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = [
            "id",
            "recipient",
            "occasion",
            "reminder_type",
            "title",
            "event_date",
            "days_before",
            "is_active",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class CheckoutSerializer(serializers.Serializer):
    promo_code = serializers.CharField(required=False, allow_blank=True, default="")


class AddToCartSerializer(serializers.Serializer):
    card_id = serializers.IntegerField()
    recipient_id = serializers.IntegerField(required=False, allow_null=True)
    delivery_method = serializers.ChoiceField(
        choices=["ecard", "post", "print"],
        default="ecard",
    )
    gift_addon_id = serializers.IntegerField(required=False, allow_null=True)
    gift_wrap = serializers.BooleanField(default=False)
    scheduled_for = serializers.DateTimeField(required=False, allow_null=True)
