# Utility Wise Enquiry API

FastAPI backend for the "Interested in Utility Wise?" contact form. Submissions are stored in
PostgreSQL - no other side effects.

## Endpoints

- `POST /api/enquiries` - submit an enquiry (name, email, company, message). Public.
- `GET /api/enquiries` - list submitted enquiries, newest first. Requires header `X-Admin-Key: <ADMIN_API_KEY>`.
- `GET /api/health` - health check.

## Setup

1. Create the database (once):

```bash
psql -U postgres -c "CREATE DATABASE utility_wise;"
```

2. Install and run the API:

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # edit DATABASE_URL / ADMIN_API_KEY as needed
uvicorn main:app --reload --port 8000
```

Tables are created automatically on startup. The API will be at `http://127.0.0.1:8000`,
interactive docs at `http://127.0.0.1:8000/docs`.

## Viewing submissions

```bash
curl -H "X-Admin-Key: <your key>" http://127.0.0.1:8000/api/enquiries
```

## Wiring the frontend

`utlitiy.html` already posts to `http://127.0.0.1:8000/api/enquiries` by default. If you deploy the
API elsewhere, update the `API_BASE` constant in the `<script>` at the bottom of the contact form
section, and set `ALLOWED_ORIGINS` in `.env` to your site's origin.
