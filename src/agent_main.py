import os

import requests
import uvicorn

from langgraph.checkpoint.memory import InMemorySaver
from fastapi import FastAPI, Header, HTTPException, status

from auth.auth import validate_access_token
from auth.quota import increment_user_usage, verify_user_quota
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
        user_info = validate_access_token(authorization)
        logger.info("User Authenticated!")
        logger.info(user_info)
    except requests.exceptions.HTTPError as e:
        raise(requests.exceptions.HTTPError, f"Error during authentication: {e}")

    # verify user quota
    user_id = user_info.get('id') or user_info.get('sub')
    quota_info = verify_user_quota(user_id, body)

    input_text = body["input_text"]
    user_query = body.get("user_query")

    if user_query is not None:
        logger.info("---------------------------------------")
        logger.info(f"Received user query: {user_query}")

    checkpointer = InMemorySaver()

    ag = DatemarkAgent(checkpointer=checkpointer,
                       llm_provider=os.environ.get("LLM_PROVIDER"),
                       llm_model=os.environ.get("LLM_MODEL"))
    response = await ag.run_datemark_agent(input_text, user_query=user_query, thread_id="foo")

    usg_increment = 1 + 1 * (user_query is not None)

    increment_user_usage(user_id=user_id, increment=usg_increment)
    logger.info(f"Remaining quota for user {user_id}: {quota_info['remaining']-usg_increment} "
                f"of {limit if (limit:=quota_info['monthly_limit'])!=-1 else '<unlimited>'} after usage")

    return response.event_list.model_dump()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
