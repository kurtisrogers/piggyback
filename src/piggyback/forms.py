from django import forms

from piggyback.models import Recipient, Reminder


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "postcode",
            "birthday",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "pb-input", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "pb-input", "placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"class": "pb-input", "placeholder": "Email"}),
            "phone": forms.TextInput(attrs={"class": "pb-input", "placeholder": "Phone"}),
            "city": forms.TextInput(attrs={"class": "pb-input", "placeholder": "City"}),
            "postcode": forms.TextInput(attrs={"class": "pb-input", "placeholder": "Postcode"}),
            "birthday": forms.DateInput(attrs={"class": "pb-input", "type": "date"}),
        }


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ["title", "reminder_type", "event_date", "days_before", "recipient"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "pb-input", "placeholder": "Reminder title"}),
            "reminder_type": forms.Select(attrs={"class": "pb-select"}),
            "event_date": forms.DateInput(attrs={"class": "pb-input", "type": "date"}),
            "days_before": forms.NumberInput(attrs={"class": "pb-input", "min": 1, "max": 90}),
            "recipient": forms.Select(attrs={"class": "pb-select"}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["recipient"].queryset = Recipient.objects.filter(owner=user)
        self.fields["recipient"].required = False
        self.fields["recipient"].empty_label = "No recipient"
