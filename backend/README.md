# UtilityWise Enquiry API

FastAPI backend for the "Interested in UtilityWise?" contact form. Submissions are stored in
PostgreSQL, and (optionally) a notification email is sent via the Gmail API whenever someone
submits the form.

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

## Gmail API notifications

Whenever a form is submitted, an email can be sent from a Gmail account you authorize to
whichever address you configure in `GMAIL_NOTIFY_TO`. This uses the Gmail API with OAuth2,
not SMTP, and needs a one-time browser authorization. It's designed to need no files at
runtime (only three env vars), so it works the same locally and on a cloud deploy like Render.

1. **Create a Google Cloud project & enable the Gmail API**
   - Go to [console.cloud.google.com](https://console.cloud.google.com/), create (or pick) a project.
   - APIs & Services -> Library -> search "Gmail API" -> Enable.

2. **Configure the OAuth consent screen**
   - APIs & Services -> OAuth consent screen -> User type "External" (or "Internal" for a
     Workspace org) -> fill app name/support email -> save.
   - Under "Test users" (if External + Testing), add the Gmail address you'll send *from*.

3. **Create an OAuth client ID**
   - APIs & Services -> Credentials -> Create Credentials -> OAuth client ID.
   - Application type: **Desktop app**.
   - Download the JSON and save it as `backend/credentials.json` (gitignored - never commit it).

4. **Authorize once, locally**

   ```bash
   cd backend
   venv\Scripts\activate
   python gmail_auth.py
   ```

   This opens a browser, asks you to log in to the Gmail account you want to send *from*, and
   grants "send email" permission. It prints a client ID, client secret, and refresh token.

5. **Set the env vars**

   Copy the three printed values into `backend/.env`:

   ```
   GMAIL_CLIENT_ID=...
   GMAIL_CLIENT_SECRET=...
   GMAIL_REFRESH_TOKEN=...
   GMAIL_NOTIFY_TO=hariharan.b@batpl.com
   ```

   For a deployed backend (e.g. Render), set the same four as environment variables on that
   service too - no files need to be uploaded.

   Leave `GMAIL_NOTIFY_TO` empty to disable notifications entirely. If the refresh token is
   ever revoked, re-run `python gmail_auth.py` and update the env vars.

## Wiring the frontend

`utlitiy.html` already posts to `http://127.0.0.1:8000/api/enquiries` by default. If you deploy the
API elsewhere, update the `API_BASE` constant in the `<script>` at the bottom of the contact form
section, and set `ALLOWED_ORIGINS` in `.env` to your site's origin.
