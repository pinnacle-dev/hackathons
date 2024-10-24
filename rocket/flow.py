from fastapi import FastAPI, Request
from rcs_types import *
from rcs import Pinnacle
from pydantic import TypeAdapter
import messages
import database
from dotenv import load_dotenv
import os
from utils import control_lock
import re

load_dotenv()

app = FastAPI()
pinn = Pinnacle(
    api_key=os.environ["PINNACLE_API_KEY"],
)
AGENT_ID = os.environ["PINNACLE_AGENT_ID"]
PINNACLE_PENTHOUSE_PASSWORD = os.environ["PINNACLE_PENTHOUSE_PASSWORD"]


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
                if selected_action == "share_wifi":
                    if re.match(r"^\d{10}$", inbound_msg.text):
                        functionality = pinn.get_rcs_functionality(
                            phone_number="+1" + inbound_msg.text
                        )
                        if dict(functionality)["is_enabled"]:
                            pinn.send.rcs(
                                from_=AGENT_ID,
                                to="+1" + inbound_msg.text,
                                **messages.wifi_msg,
                            )
                        else:
                            print("+1" + inbound_msg.text)
                            pinn.send.mms(
                                from_=os.environ["SMS_NUMBER"],
                                to="+1" + inbound_msg.text,
                                text="Press and hold the WiFi icon to connect to the network.",
                                media_urls=[
                                    "https://i.ibb.co/CnXB6tc/pinnacle-wifi.png",
                                ],
                            )

                        print(f"WiFi message sent to +1{inbound_msg.text}")

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
        if action == "get_wifi":
            pinn.send.rcs(
                from_=AGENT_ID,
                to=fromNumber,
                text="Press and hold the WiFi icon to connect to the network.",
            )
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.wifi_msg)
            print(f"WiFi QR code sent to {fromNumber}")
        elif action == "restart":
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.intro_msg)
            print(f"Intro message sent to {fromNumber}")
        elif action == "share_wifi":
            pinn.send.rcs(
                from_=AGENT_ID,
                to=fromNumber,
                text="Please enter the 10-digit phone number to share the WiFi password with. For example 1234567890",
            )
            print(f"Share WiFi message sent to {fromNumber}")
        elif action == "lock_door" or action == "unlock_door":
            print(f"Door {action} action requested")
            if inbound_msg.actionMetadata:
                if inbound_msg.actionMetadata == PINNACLE_PENTHOUSE_PASSWORD:
                    await control_lock(locked=action == "lock_door")
                    pinn.send.rcs(
                        from_=AGENT_ID,
                        to=fromNumber,
                        text="The door is now"
                        + (" locked." if action == "lock_door" else " unlocked.")
                        + " Welcome to the Pinnacle Penthouse 🦝",
                        quick_replies=messages.base_actions,
                    )
                else:
                    pinn.send.rcs(
                        from_=AGENT_ID,
                        to=fromNumber,
                        text="Incorrect password. Please try again.",
                        quick_replies=messages.create_combinations(action),
                    )
            else:
                pinn.send.rcs(
                    from_=AGENT_ID,
                    to=fromNumber,
                    text="What is the correct combination?",
                    quick_replies=messages.create_combinations(action),
                )
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
