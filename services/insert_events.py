import os
import uvicorn
from typing import Optional

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware

import logging

from src.services.google_calendar import create_calendar_event
from src.services.google_authentication import create_oauth_credentials_from_token, create_oauth_flow_with_credentials
from models.io_models import Event

logger = logging.getLogger()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["chrome-extension://*"] but * is easier
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/events")
async def insert_events(body: dict, authorization: Optional[str] = Header(None)):
    id_token = authorization.split('Bearer ')[1]

    events = body["events"]

    logging.info("ENTRO QUI")

    creds = create_oauth_credentials_from_token(id_token)

    logger.info(f"Inserting the following Events:\n{str(events)}")

    for ev in events:
        create_calendar_event(creds, Event(**ev))

    return {"event_list": events}


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
