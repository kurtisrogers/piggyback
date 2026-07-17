from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load sample occasion categories, templates, and assets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            action="store_true",
            help="Load from src/piggyback/fixtures/sample_data.json instead of generating.",
        )

    def handle(self, *args, **options):
        if options["fixture"]:
            self.stdout.write("Loading Piggyback fixtures...")
            call_command("loaddata", "sample_data", app_label="piggyback")
            self.stdout.write(self.style.SUCCESS("Fixtures loaded successfully."))
            return

        from piggyback.models import (
            CardStyle,
            CardTemplate,
            DesignAsset,
            GiftAddon,
            Occasion,
            OccasionCategory,
        )

        self.stdout.write("Loading Piggyback sample data...")

        categories_data = [
            ("birthday", "Birthday", "🎂", "#FF6B6B", True, 1),
            ("wedding", "Wedding & Anniversary", "💍", "#C9A0DC", True, 2),
            ("new-baby", "New Baby", "👶", "#87CEEB", True, 3),
            ("sympathy", "Sympathy", "🕊️", "#A8A8A8", False, 4),
            ("thank-you", "Thank You", "🙏", "#98D8C8", True, 5),
            ("christmas", "Christmas", "🎄", "#E74C3C", True, 6),
            ("valentines", "Valentine's Day", "❤️", "#E85D75", True, 7),
            ("graduation", "Graduation", "🎓", "#F39C12", False, 8),
        ]

        for slug, name, icon, color, featured, order in categories_data:
            OccasionCategory.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "icon": icon,
                    "color": color,
                    "is_featured": featured,
                    "sort_order": order,
                    "description": f"Beautiful cards for {name.lower()} occasions.",
                },
            )

        occasions_data = [
            ("birthday", "birthday-general", "Birthday", CardStyle.FUNNY),
            ("birthday", "21st-birthday", "21st Birthday", CardStyle.FUNNY),
            ("birthday", "milestone-birthday", "Milestone Birthday", CardStyle.TRADITIONAL),
            ("wedding", "wedding-day", "Wedding Day", CardStyle.LUXURY),
            ("wedding", "anniversary", "Anniversary", CardStyle.TRADITIONAL),
            ("new-baby", "new-baby-boy", "New Baby Boy", CardStyle.PHOTO),
            ("new-baby", "new-baby-girl", "New Baby Girl", CardStyle.PHOTO),
            ("sympathy", "with-sympathy", "With Sympathy", CardStyle.TRADITIONAL),
            ("thank-you", "thank-you-general", "Thank You", CardStyle.TRADITIONAL),
            ("christmas", "merry-christmas", "Merry Christmas", CardStyle.TRADITIONAL),
            ("valentines", "valentines-day", "Valentine's Day", CardStyle.LUXURY),
            ("graduation", "congratulations-grad", "Congratulations Graduate", CardStyle.FUNNY),
        ]

        for cat_slug, occ_slug, name, style in occasions_data:
            category = OccasionCategory.objects.get(slug=cat_slug)
            occasion, _ = Occasion.objects.update_or_create(
                slug=occ_slug,
                defaults={"name": name, "category": category},
            )
            CardTemplate.objects.update_or_create(
                slug=f"{occ_slug}-classic",
                defaults={
                    "name": f"{name} — Classic",
                    "occasion": occasion,
                    "style": style,
                    "description": f"A classic {name.lower()} card design.",
                    "is_active": True,
                    "popularity_score": 100,
                    "canvas_data": {
                        "version": "5.3.0",
                        "background": "#FFF8F0",
                        "objects": [
                            {
                                "type": "text",
                                "text": name.upper(),
                                "left": 874,
                                "top": 400,
                                "fontSize": 72,
                                "fill": "#2D2D2D",
                                "fontFamily": "Georgia",
                                "originX": "center",
                                "textAlign": "center",
                            },
                            {
                                "type": "text",
                                "text": "With love",
                                "left": 874,
                                "top": 2000,
                                "fontSize": 36,
                                "fill": "#666666",
                                "fontFamily": "Georgia",
                                "originX": "center",
                            },
                        ],
                    },
                },
            )

        gifts = [
            ("Belgian Chocolates", "Luxury Belgian truffles, 200g", 599),
            ("Scented Candle", "Lavender & vanilla, 40hr burn", 899),
            ("Mini Prosecco", "200ml bottle, ready to celebrate", 799),
        ]
        for name, desc, price in gifts:
            GiftAddon.objects.update_or_create(
                name=name,
                defaults={"description": desc, "price_pence": price, "is_active": True},
            )

        stickers = ["🎈", "🎉", "⭐", "🌸", "🦋", "🎁"]
        for emoji in stickers:
            DesignAsset.objects.update_or_create(
                name=f"Sticker {emoji}",
                defaults={"asset_type": DesignAsset.AssetType.STICKER, "tags": "sticker,fun"},
            )

        self.stdout.write(self.style.SUCCESS("Sample data loaded successfully."))
