"""One-time setup script: authorizes this app to send email as your Gmail account.

Run this locally (it opens a browser window):

    python gmail_auth.py

It reads the OAuth client secret from credentials.json (downloaded from Google Cloud
Console) and prints the client ID, client secret, and refresh token. Copy those three
values into GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET / GMAIL_REFRESH_TOKEN - in backend/.env
for local use, and as environment variables on your deploy platform (e.g. Render) for
production. No files need to be present at runtime; the server builds credentials
directly from these three values plus a refresh call, so this works identically
locally and on a cloud deploy with an ephemeral filesystem.

Re-run this script (and update the env vars) if the refresh token is ever revoked.
"""

from google_auth_oauthlib.flow import InstalledAppFlow

from gmail_service import SCOPES

CREDENTIALS_FILE = "credentials.json"


def main():
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    print()
    print("Authorization complete. Set these as environment variables:")
    print()
    print(f"GMAIL_CLIENT_ID={creds.client_id}")
    print(f"GMAIL_CLIENT_SECRET={creds.client_secret}")
    print(f"GMAIL_REFRESH_TOKEN={creds.refresh_token}")


if __name__ == "__main__":
    main()
