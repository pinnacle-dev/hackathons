from fastapi import FastAPI, Request
from rcs_types import *
from rcs import Pinnacle
from pydantic import TypeAdapter
import messages
import database
from dotenv import load_dotenv
import os
from stalk import stalk

load_dotenv()

app = FastAPI()
pinn = Pinnacle(
    api_key=os.environ["PINNACLE_API_KEY"],
)
AGENT_ID = os.environ["PINNACLE_AGENT_ID"]


@app.post("/")
async def receive_msg(request: Request):
    json_data = await request.json()
    if (
        request.headers.get("pinnacle-signing-secret")
        != os.environ["PINNACLE_SIGNING_SECRET"]
    ):
        print("Invalid signing secret")
        return

    inbound_msg = TypeAdapter(InboundMessage).validate_python(json_data)

    fromNumber = inbound_msg.from_

    if not fromNumber:
        print("No fromNumber found in payload")
        return

    message_history = database.get(fromNumber)
    if isinstance(inbound_msg, InboundTextMessage):
        if message_history and len(message_history) > 0:
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **stalk(inbound_msg.text))
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.outro_msg)
            print(f"Stalk message sent to {fromNumber}")
        else:
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.intro_msg)
            print(f"Intro message sent to {fromNumber}")
    else:
        pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg)

    if not message_history:
        database.set(fromNumber, inbound_msg)
    else:
        message_history.append(inbound_msg)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("flow:app", host="0.0.0.0", port=8000, reload=True)
