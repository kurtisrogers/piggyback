from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "example.accounts"
    label = "example_accounts"
    verbose_name = "Example Accounts"
