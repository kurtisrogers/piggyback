# Quick Start

Get Piggyback running in under five minutes.

## 1. Run the example project

```bash
cd piggyback
pip install -e ".[dev]"
cd example
python manage.py migrate
python manage.py load_sample_data
python manage.py createsuperuser
python manage.py runserver
```

## 2. Browse the card shop

Open [http://localhost:8000/catalog/](http://localhost:8000/catalog/) to browse templates by occasion and style.

## 3. Design a card

Click any template to open the card editor. You can:

- Add and edit text (double-click)
- Upload photos
- Add emoji stickers
- Change background colours
- Write an inside message

Sign in via `/admin/login/` to save your design.

## 4. Send a card

1. Save your design in the editor
2. Add a recipient via the API or admin
3. Add to cart and checkout
4. Use promo code `FIRSTCARD` for a free e-card

## 5. Explore the API

```bash
# List templates
curl http://localhost:8000/api/templates/

# Personalise a template (authenticated)
curl -X POST http://localhost:8000/api/templates/birthday-general-classic/personalize/ \
  -H "Cookie: sessionid=YOUR_SESSION"
```

## 6. Set up reminders

```bash
# Add to crontab — runs daily
0 9 * * * cd /path/to/project && python manage.py send_reminders
```
