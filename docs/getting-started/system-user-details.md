# System user details integration

Piggyback can read name, email, address, and other contact fields directly from your existing Django `User` model and related profile — no duplicate data entry.

## How it works

1. **Adapter** — `DefaultUserDetailsAdapter` maps host model fields to Piggyback's normalised `UserDetails`
2. **Auto-sync** — On login and when listing recipients, Piggyback creates/updates a special address-book entry (`is_system_user=True`) from the system profile
3. **Sender display** — E-cards and reminders use the adapter for the sender's display name and email

## Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `PIGGYBACK_USE_SYSTEM_USER_DETAILS` | `True` | Read details via the adapter |
| `PIGGYBACK_AUTO_SYNC_USER_RECIPIENT` | `True` | Sync an address-book entry from system user |
| `PIGGYBACK_USER_DETAILS_ADAPTER` | `piggyback.adapters.user_details.DefaultUserDetailsAdapter` | Adapter class path |
| `PIGGYBACK_USER_PROFILE_RELATION` | `None` | Related profile accessor, e.g. `"profile"` |
| `PIGGYBACK_USER_FIELD_MAP` | `email`, `first_name`, `last_name` | User model field mapping |
| `PIGGYBACK_PROFILE_FIELD_MAP` | `{}` | Profile model field mapping |

## Example: User + Profile model

```python
# settings.py
PIGGYBACK_USER_PROFILE_RELATION = "profile"
PIGGYBACK_PROFILE_FIELD_MAP = {
    "phone": "phone_number",
    "address_line_1": "line1",
    "address_line_2": "line2",
    "city": "city",
    "county": "county",
    "postcode": "postcode",
    "country": "country",
    "birthday": "birthday",
}
```

The example project includes `example.accounts.UserProfile` with this configuration.

## Example: fields on User model only

If your user model has all fields directly (no separate profile):

```python
PIGGYBACK_USER_PROFILE_RELATION = None
PIGGYBACK_USER_FIELD_MAP = {
    "email": "email",
    "first_name": "first_name",
    "last_name": "last_name",
    "phone": "mobile",
    "address_line_1": "home_address",
    "city": "home_city",
    "postcode": "home_postcode",
}
```

## Custom adapter

For complex setups (multiple profiles, external CRM, etc.), subclass `BaseUserDetailsAdapter`:

```python
# myapp/piggyback_adapter.py
from piggyback.adapters.user_details import BaseUserDetailsAdapter, UserDetails

class MyUserDetailsAdapter(BaseUserDetailsAdapter):
    def get_user_details(self, user):
        crm = user.crm_contact  # your existing model
        return UserDetails(
            first_name=crm.given_name,
            last_name=crm.family_name,
            email=crm.email_address,
            phone=crm.mobile,
            address_line_1=crm.street,
            city=crm.town,
            postcode=crm.zip,
        )
```

```python
# settings.py
PIGGYBACK_USER_DETAILS_ADAPTER = "myapp.piggyback_adapter.MyUserDetailsAdapter"
```

## API

```bash
# Read resolved system user details
GET /api/me/details/

# Force sync to address book
POST /api/me/sync_recipient/
```

The synced address-book entry has `is_system_user: true` and cannot be deleted via the API (it is refreshed from your system profile).

## Disabling sync

```python
PIGGYBACK_USE_SYSTEM_USER_DETAILS = False
PIGGYBACK_AUTO_SYNC_USER_RECIPIENT = False
```

Piggyback falls back to basic `User.email`, `first_name`, and `last_name` only.
