import os

import requests
import uvicorn

from langgraph.checkpoint.memory import InMemorySaver
from fastapi import FastAPI, Header, HTTPException, status

from auth.auth import validate_access_token
from auth.quota import get_or_create_user_quota, increment_user_usage
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
    quota_info = get_or_create_user_quota(user_id=user_id)

    logger.info(quota_info)

    if quota_info["remaining"] == -1:
        logger.info(f"User {user_id} has unlimited plan: access granted!")

    elif quota_info['remaining'] < 1:
        logger.info(f"Exceeded quota for user {user_id}: raising HTTP Error")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Period quota exceeded. Please contact the developer at: infodatemark@gmail.com.",
            headers={"Retry-After": "2592000"}  # Seconds until next month (optional)
        )

    logger.info(f"Remaining quota for user {user_id}: {quota_info['remaining']} "
                f"of {limit if (limit:=quota_info['monthly_limit'])!=-1 else '<unlimited>'}")

    input_text = body["input_text"]
    logger.info(f"Received input text: {input_text}")

    checkpointer = InMemorySaver()

    ag = DatemarkAgent(checkpointer=checkpointer,
                       llm_provider=os.environ.get("LLM_PROVIDER"),
                       llm_model=os.environ.get("LLM_MODEL"))
    response = await ag.run_datemark_agent(input_text, thread_id="foo")

    increment_user_usage(user_id=user_id)
    logger.info(f"Remaining quota for user {user_id}: {quota_info['remaining']-1} "
                f"of {limit if (limit:=quota_info['monthly_limit'])!=-1 else '<unlimited>'} after usage")

    return response.event_list.model_dump()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
