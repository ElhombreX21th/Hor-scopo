# SeuFuturo

Astrology prediction SaaS with a FastAPI backend, responsive PWA frontend, authentication, plan-based paywall, and recurring subscription flow.

## Screenshots

![SeuFuturo app preview](screenshot-1.svg)

![SeuFuturo second preview](preview-2.svg)

## Structure

```text
SeuFuturo/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── test_main.py
├── frontend/
│   ├── index.html
│   ├── manifest.json
│   ├── service-worker.js
│   ├── privacy.html
│   └── terms.html
├── screenshot-1.svg
├── preview-2.svg
└── README.md
```

## Local Setup

Backend:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Frontend:

```bash
python -m http.server 8001 --directory frontend
```

Local URLs:

- Frontend: `http://127.0.0.1:8001`
- Backend: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

## Features

- Responsive PWA frontend
- FastAPI backend
- Authentication
- Plan control
- Checkout flow
- Terms and privacy pages
- Automated tests

## Plans

| Plan | Features |
|---|---|
| Basic | Daily prediction |
| Premium | Love + career |
| VIP | Everything + luck and mystic advice |

## Main Endpoints

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/me`
- `GET /api/horoscopo`
- `POST /api/checkout/session`
- `POST /api/billing/portal`

## Tests

```bash
pytest backend/test_main.py -q
```

## Status

MVP SaaS/PWA project. Before real traffic, replace local storage with an external database, review security, configure production environment variables, and validate the full payment flow.
