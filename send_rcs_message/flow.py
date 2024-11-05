from fastapi import FastAPI, Request
from rcs_types import *
from pydantic import TypeAdapter
from rcs import Pinnacle
import messages
import database
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

app = FastAPI()
pinn = Pinnacle(
    api_key=os.environ["PINNACLE_API_KEY"],
)
AGENT_ID = os.environ["PINNACLE_AGENT_ID"]


@app.post("/general_rcs")
async def receive_msg(request: Request):
    json_data = await request.json()
    if (
        request.headers.get("pinnacle-signing-secret")
        != os.environ["PINNACLE_SIGNING_SECRET"]
    ):
        print("Invalid signing secret")
        return

    inbound_msg = TypeAdapter(InboundMessage).validate_python(json_data)
    print(inbound_msg)

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
                if selected_action == "check_rcs_functionality":
                    if re.match(r"^\d{10}$", inbound_msg.text):
                        functionality = pinn.get_rcs_functionality(
                            phone_number="+1" + inbound_msg.text
                        )
                        pinn.send.rcs(
                            from_=AGENT_ID,
                            to=fromNumber,
                            **messages.create_rcs_capability_msg(functionality),
                        )

                        print(f"RCS functionality message sent to {fromNumber}")
                    else:
                        pinn.send.rcs(
                            from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg
                        )
                        print(f"Error message sent to {fromNumber}")
                elif selected_action == "send_rcs_message":
                    if re.match(r"^\d{10}$", inbound_msg.text):
                        pinn.send.rcs(
                            from_=AGENT_ID,
                            to=fromNumber,
                            **messages.create_send_rcs_message_with_payload(
                                "+1" + inbound_msg.text
                            ),
                        )

                        print(f"RCS functionality message sent to {fromNumber}")
                    else:
                        pinn.send.rcs(
                            from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg
                        )
                        print(f"Error message sent to {fromNumber}")
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

        try:
            rcs_msg_type = json.loads(action) if action else None
        except json.JSONDecodeError:
            rcs_msg_type = None

        if rcs_msg_type and rcs_msg_type["type"] and rcs_msg_type["to"]:
            if rcs_msg_type["type"] == "send_text_message":
                pinn.send.rcs(
                    from_=AGENT_ID, to=rcs_msg_type["to"], **messages.intro_msg
                )
                print(f"Text message sent to {rcs_msg_type['to']}")
            elif rcs_msg_type["type"] == "send_media_message":
                pinn.send.rcs(
                    from_=AGENT_ID,
                    to=rcs_msg_type["to"],
                    **messages.media_msg,
                )
            elif rcs_msg_type["type"] == "send_carousel":
                pinn.send.rcs(
                    from_=AGENT_ID,
                    to=rcs_msg_type["to"],
                    **messages.pinnacle_carousel_msg,
                )
                print(f"Carousel message sent to {rcs_msg_type['to']}")
            return

        if action == "check_rcs_functionality":
            pinn.send.rcs(
                from_=AGENT_ID,
                to=fromNumber,
                text="Please enter the 10-digit phone number you would like to check for RCS functionality. For example 1234567890",
            )
            print(f"Check RCS functionality message sent to {fromNumber}")
        elif action == "read_more":
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.read_more)
            print(f"Read more message sent to {fromNumber}")
        elif action == "send_rcs_message":
            pinn.send.rcs(
                from_=AGENT_ID,
                to=fromNumber,
                text="Please enter the 10-digit phone number you would like to send an RCS message to. For example 1234567890",
            )
            print(f"Send RCS message sent to {fromNumber}")
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
