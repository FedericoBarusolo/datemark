import os

import requests
import uvicorn

from langgraph.checkpoint.memory import InMemorySaver
from fastapi import FastAPI, Header

from auth.auth import validate_access_token
from agents.datemark_agent import DatemarkAgent

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["chrome-extension://*"] but * is easier
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/agent")
async def datemark_agent(body: dict, authorization: str = Header(...)):

    # authorization performed at code-level to avoid identity token exposure to the network
    try:
        validate_access_token(authorization)
    except requests.exceptions.HTTPError as e:
        raise(requests.exceptions.HTTPError, f"Error during authentication: {e}")

    input_text = body["input_text"]
    logger.info(f"Received input text: {input_text}")

    checkpointer = InMemorySaver()

    ag = DatemarkAgent(checkpointer=checkpointer,
                       llm_provider=os.environ.get("LLM_PROVIDER"),
                       llm_model=os.environ.get("LLM_MODEL"))
    response = await ag.run_datemark_agent(input_text, thread_id="foo")

    return response.event_list.model_dump()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
