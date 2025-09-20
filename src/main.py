import os
import json
import uvicorn

from langgraph.checkpoint.memory import InMemorySaver
from fastapi import FastAPI

from agents.datemark_agent import DatemarkAgent

import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()


@app.post("/agent")
async def datemark_agent(request: dict):
    input_text = request["input_text"]

    print(f"Received input text: {input_text}")

    thread_id = "prova1"
    checkpointer = InMemorySaver()

    ag = DatemarkAgent(checkpointer=checkpointer)

    response = await ag.run_datemark_agent(input_text, thread_id)

    return response.event_list.model_dump()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
