import pytest

from piggyback.models import Card, CardTemplate, Occasion, OccasionCategory, Order, Recipient
from piggyback.services.checkout import add_card_to_cart, complete_payment


@pytest.fixture
def category(db):
    return OccasionCategory.objects.create(name="Birthday", slug="birthday", icon="🎂")


@pytest.fixture
def occasion(category):
    return Occasion.objects.create(name="Birthday", slug="birthday-general", category=category)


@pytest.fixture
def template(occasion):
    return CardTemplate.objects.create(
        name="Birthday Classic",
        slug="birthday-classic",
        occasion=occasion,
        canvas_data={"background": "#FFF8F0", "objects": []},
    )


@pytest.fixture
def card(user, template):
    return Card.objects.create(
        owner=user,
        template=template,
        title="Test Card",
        canvas_data=template.canvas_data,
    )


@pytest.fixture
def recipient(user):
    return Recipient.objects.create(
        owner=user,
        first_name="Bob",
        last_name="Smith",
        email="bob@example.com",
    )


@pytest.mark.django_db
class TestCatalogAPI:
    def test_list_categories(self, api_client, category):
        response = api_client.get("/api/categories/")
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_list_templates(self, api_client, template):
        response = api_client.get("/api/templates/")
        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_personalize_template(self, api_client, template, user):
        response = api_client.post(f"/api/templates/{template.slug}/personalize/")
        assert response.status_code == 201
        assert Card.objects.filter(owner=user).count() == 1


@pytest.mark.django_db
class TestCardAPI:
    def test_create_card(self, api_client, user):
        response = api_client.post(
            "/api/cards/", {"title": "My Card", "canvas_data": {}}, format="json"
        )
        assert response.status_code == 201
        assert Card.objects.filter(owner=user, title="My Card").exists()

    def test_save_design(self, api_client, card):
        response = api_client.post(
            f"/api/cards/{card.id}/save_design/",
            {"canvas_data": {"objects": []}, "inside_message": "Hello!"},
            format="json",
        )
        assert response.status_code == 200
        card.refresh_from_db()
        assert card.inside_message == "Hello!"
        assert card.status == "saved"


@pytest.mark.django_db
class TestCheckout:
    def test_add_to_cart(self, user, card, recipient):
        item = add_card_to_cart(user, card, recipient=recipient, delivery_method="ecard")
        assert item.order.status == Order.OrderStatus.CART
        assert item.line_total_pence > 0

    def test_complete_payment(self, user, card, recipient):
        item = add_card_to_cart(user, card, recipient=recipient)
        order = item.order
        order.status = Order.OrderStatus.PENDING_PAYMENT
        order.recalculate_totals()
        order.save()
        complete_payment(order)
        order.refresh_from_db()
        assert order.status == Order.OrderStatus.COMPLETED


@pytest.mark.django_db
class TestRecipients:
    def test_create_recipient(self, api_client, user):
        response = api_client.post(
            "/api/recipients/",
            {"first_name": "Jane", "last_name": "Doe", "email": "jane@example.com"},
        )
        assert response.status_code == 201
        # Includes auto-synced system user entry when enabled
        assert Recipient.objects.filter(owner=user, is_system_user=False).count() == 1


@pytest.mark.django_db
class TestLibrary:
    def test_library_auto_populated(self, card):
        from piggyback.models import CardLibraryEntry

        entries = CardLibraryEntry.objects.filter(user=card.owner)
        assert entries.exists()


@pytest.mark.django_db
class TestSystemUserDetails:
    def test_get_user_details_from_user_model(self, user):
        from piggyback.adapters import get_user_details

        details = get_user_details(user)
        assert details.email == "alice@example.com"
        assert details.first_name == "Alice"
        assert details.last_name == "Anderson"

    def test_get_user_details_from_profile(self, user):
        from example.accounts.models import UserProfile
        from piggyback.adapters import get_user_details

        UserProfile.objects.create(
            user=user,
            phone_number="07700900123",
            line1="1 High Street",
            city="London",
            postcode="SW1A 1AA",
        )
        details = get_user_details(user)
        assert details.phone == "07700900123"
        assert details.address_line_1 == "1 High Street"
        assert details.city == "London"
        assert details.postcode == "SW1A 1AA"

    def test_sync_user_recipient(self, user):
        from example.accounts.models import UserProfile
        from piggyback.adapters import sync_user_recipient

        UserProfile.objects.create(
            user=user,
            line1="1 High Street",
            city="London",
            postcode="SW1A 1AA",
        )
        recipient = sync_user_recipient(user)
        assert recipient is not None
        assert recipient.is_system_user is True
        assert recipient.address_line_1 == "1 High Street"

        user.first_name = "Alicia"
        user.save()
        recipient = sync_user_recipient(user)
        assert recipient.first_name == "Alicia"

    def test_me_details_api(self, api_client, user):
        response = api_client.get("/api/me/details/")
        assert response.status_code == 200
        assert response.data["email"] == "alice@example.com"
        assert response.data["full_name"] == "Alice Anderson"

    def test_sync_recipient_api(self, api_client, user):
        response = api_client.post("/api/me/sync_recipient/")
        assert response.status_code == 200
        assert response.data["is_system_user"] is True

    def test_cannot_delete_system_recipient(self, api_client, user):
        from piggyback.adapters import sync_user_recipient

        recipient = sync_user_recipient(user)
        response = api_client.delete(f"/api/recipients/{recipient.id}/")
        assert response.status_code == 403
        assert Recipient.objects.filter(id=recipient.id).exists()
