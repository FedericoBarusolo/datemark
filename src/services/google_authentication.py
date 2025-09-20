import os
import dotenv

from google_auth_oauthlib.flow import InstalledAppFlow

dotenv.load_dotenv()

config_file = {
    "web": {"client_id": os.environ.get("G_CLIENT_ID"),
            "project_id": os.environ.get("G_PROJECT_ID"),
            "auth_uri": os.environ.get("G_AUTH_URI"),
            "token_uri": os.environ.get("G_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get("G_AUTH_PROVIDER"),
            "client_secret": os.environ.get("G_CLIENT_SECRET")}
}


# Set up OAuth flow
def create_oauth_flow_with_credentials():
    flow = InstalledAppFlow.from_client_config(config_file, scopes=['https://www.googleapis.com/auth/calendar'])
    creds = flow.run_local_server(port=8080)
    return creds
