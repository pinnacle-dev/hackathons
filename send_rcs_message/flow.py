from fastapi import FastAPI, Request
from rcs_types import PayloadData
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


@app.post("/")
async def receive_msg(request: Request):
    json_data = await request.json()
    payload = PayloadData(**json_data)

    fromNumber = (
        payload.messagePayload.fromNum
        if payload.messagePayload
        else payload.buttonPayload.fromNum if payload.buttonPayload else None
    )

    if not fromNumber:
        print("No fromNumber found in payload")
        return

    message_history = database.get(fromNumber)
    if payload.messagePayload and payload.messagePayload.text:
        if message_history and len(message_history) > 0:
            prev_action = message_history[-1]
            if prev_action.buttonPayload:
                selected_action = prev_action.buttonPayload.payload
                if selected_action == "check_rcs_functionality":
                    if re.match(r"^\d{10}$", payload.messagePayload.text):
                        functionality = pinn.get_rcs_functionality(
                            phone_number="+1" + payload.messagePayload.text
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
                    if re.match(r"^\d{10}$", payload.messagePayload.text):
                        pinn.send.rcs(
                            from_=AGENT_ID,
                            to=fromNumber,
                            **messages.create_send_rcs_message_with_payload(
                                "+1" + payload.messagePayload.text
                            ),
                        )

                        print(f"RCS functionality message sent to {fromNumber}")
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
    elif payload.buttonPayload and payload.buttonPayload.payload:
        action = payload.buttonPayload.payload

        try:
            rcs_msg_type = json.loads(action)
            print(rcs_msg_type, rcs_msg_type["type"], rcs_msg_type["to"])
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
        database.set(fromNumber, payload)
    else:
        message_history.append(payload)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("flow:app", host="0.0.0.0", port=8000, reload=True)
