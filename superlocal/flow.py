from fastapi import FastAPI, Request
from rcs_types import *
from rcs import Pinnacle
from pydantic import TypeAdapter
import messages
import database
from dotenv import load_dotenv
import os
from search import search

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
            prev_action = message_history[-1]
            if isinstance(prev_action, InboundActionMessage):
                selected_action = prev_action.payload
                if selected_action in messages.search_actions_dict:
                    pinn.send.rcs(
                        from_=AGENT_ID,
                        to=fromNumber,
                        **messages.create_request_location_msg(selected_action),
                    )
                    print(f"Request location message sent to {fromNumber}")
                else:
                    pinn.send.rcs(
                        from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg
                    )
                    print(f"Error message sent to {fromNumber}")
            else:
                pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg)
                print(f"Error message sent to {fromNumber}")
        else:
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.intro_msg)
            print(f"Intro message sent to {fromNumber}")
    elif isinstance(inbound_msg, InboundActionMessage):
        action = inbound_msg.payload
        if action == "superlocal":
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.intro_msg)
            print(f"Intro message sent to {fromNumber}")
        elif action in messages.search_actions_dict:
            pinn.send.rcs(
                from_=AGENT_ID,
                to=fromNumber,
                **messages.create_request_location_msg(action),
            )
            print(f"Request location message sent to {fromNumber}")
        elif inbound_msg.actionTitle == "Send Location" and inbound_msg.payload == None:
            return
        else:
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg)
            print(f"Error message sent to {fromNumber}")

    elif isinstance(inbound_msg, InboundLocationMessage):
        currLocation = inbound_msg.coordinates
        if message_history and len(message_history) > 0:
            prev_action = message_history[-1]
            if isinstance(prev_action, InboundActionMessage):
                selected_action = prev_action.payload
                if selected_action in messages.search_actions_dict:
                    pinn.send.rcs(
                        from_=AGENT_ID,
                        to=fromNumber,
                        **search(selected_action, currLocation),
                    )
                else:
                    pinn.send.rcs(
                        from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg
                    )
                    print(f"Error message sent to {fromNumber}")
            else:
                pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg)
                print(f"Error message sent to {fromNumber}")
        else:
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg)
            print(f"Error message sent to {fromNumber}")

    else:
        pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg)

    if not message_history:
        database.set(fromNumber, inbound_msg)
    else:
        message_history.append(inbound_msg)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("flow:app", host="0.0.0.0", port=8000, reload=True)
