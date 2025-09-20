import os
import uvicorn
import requests
from google.auth.transport import requests as google_requests
from google.auth import compute_engine
import google.auth
from google.oauth2 import id_token

from typing import Optional

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware

import logging
logger = logging.getLogger()

# Your protected Cloud Run service URL
TARGET_AUDIENCE = "https://{}-852615838189.europe-west1.run.app"

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["chrome-extension://*"] but * is easier
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/exchange")
async def exchange_token(body: dict, authorization: Optional[str] = Header(None)):
    oauth_token = authorization.split('Bearer ')[1]

    target_name = body["target_name"]

    #try:
        # Validate the OAuth token
    token_info = requests.get(
        'https://oauth2.googleapis.com/tokeninfo',
        params={'access_token': oauth_token}
    )
    token_info.raise_for_status()

    # Use the access token to get an identity token
    # This creates an authenticated request using the access token
    auth_req = google_requests.Request()

    # Get identity token for the target audience
    id_token_val = id_token.fetch_id_token(auth_req, TARGET_AUDIENCE.format(target_name))

    return {
        "id_token": id_token_val,
        "target_audience": TARGET_AUDIENCE.format(target_name)
    }


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
