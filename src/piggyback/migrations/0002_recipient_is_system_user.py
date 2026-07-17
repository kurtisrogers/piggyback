# Generated migration for system user recipient sync

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("piggyback", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipient",
            name="is_system_user",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "True when this entry is synced from the owner's system user profile."
                ),
            ),
        ),
        migrations.AddConstraint(
            model_name="recipient",
            constraint=models.UniqueConstraint(
                condition=models.Q(is_system_user=True),
                fields=("owner",),
                name="piggyback_unique_system_user_recipient",
            ),
        ),
    ]
