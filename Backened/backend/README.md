# Backend — Local Development

Quick steps to get the Django backend running locally (development).

Prerequisites
- Python 3.11+
- Git
- (optional) Docker / Docker Compose

Create a virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Environment
- Copy `.env.example` to `.env` and set values. For quick local work you can use SQLite (the default in `settings.py`).

Email webhook (n8n)
- To send emails via an n8n webhook instead of SMTP, set these environment variables in your `.env`:
	- `EMAIL_USE_WEBHOOK=True` (default: True)
	- `EMAIL_WEBHOOK_URL=https://n8n.example.com/webhook/send-email-mobile-mechanics`

The backend will POST JSON `{to, subject, body, reply_to}` to the webhook. If the webhook is not configured, the code falls back to Django's `send_mail`.

Database and migrations
```bash
python manage.py migrate
```

Create a superuser (interactive)
```bash
python manage.py createsuperuser
```

Run tests
```bash
python manage.py test
```

Run development server
```bash
python manage.py runserver
```

Notes
- If you prefer Docker for local dev, the project already contains `docker-compose` definitions under `Backened/`; adapt as needed.
- For OTP/auth endpoints, consult `users` app and `mobilemechanic/urls.py` for exact routes.
