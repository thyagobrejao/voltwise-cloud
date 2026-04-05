# VoltWise Cloud

Central Django backend for the VoltWise EV charging SaaS platform.

## 🛠️ Tech Stack

- Python 3.12+
- Django 5 · Django REST Framework
- PostgreSQL
- Redis + Celery (task queue structure)
- JWT authentication (djangorestframework-simplejwt)

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your DB credentials and secret key

# 3. Apply migrations
python manage.py migrate

# 4. Create a superuser
python manage.py createsuperuser

# 5. Run development server
python manage.py runserver
```

## 🧪 Running Tests

```bash
# Django test runner
python manage.py test

# Or with pytest
pytest
```

## 📁 Project Structure

```
voltwise-cloud/
  config/
    settings/
      base.py      # shared settings
      dev.py       # development overrides
      prod.py      # production overrides
    urls.py
    celery.py
  apps/
    common/        # BaseModel, permissions, pagination
    users/         # Custom User model + JWT auth endpoints
    organizations/ # Multi-tenant organization management
    chargers/      # Charger models + OCPP integration layer
    sessions/      # Charging session tracking
    billing/       # Placeholder for billing features
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new user |
| POST | `/api/auth/login/` | Obtain JWT token pair |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET  | `/api/users/me/` | Current user profile |
| GET/POST | `/api/organizations/` | List / create organizations |
| GET/POST | `/api/chargers/` | List / create chargers |
| PATCH | `/api/chargers/{id}/` | Update a charger |
| GET | `/api/sessions/` | List charging sessions |
| GET | `/api/sessions/{id}/` | Session detail |

### Internal endpoints (voltwise-ocpp only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/internal/chargers/{id}/status/` | Update charger status |
| POST | `/api/internal/sessions/` | Open a new session |
| POST | `/api/internal/sessions/stop/` | Close a session |
| POST | `/api/internal/sessions/meter-values/` | Record meter value |

Internal endpoints require the `X-Internal-Api-Key` header.

## 📖 Documentation

See [voltwise-docs/cloud/architecture.md](../voltwise-docs/cloud/architecture.md).
- Redis
- Celery

## 🔗 Integrations

- voltwise-core
- voltwise-ocpp
- voltwise-agent

## 🚀 Goal

Serve as the central brain of the VoltWise ecosystem.

## 📄 License

AGPL v3
