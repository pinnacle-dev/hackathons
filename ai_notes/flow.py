from fastapi import FastAPI, Request
from rcs_types import *
from rcs import Pinnacle
from pydantic import TypeAdapter
from dotenv import load_dotenv
import os
from datetime import datetime
import messages
from ai import get_date, summarize_notes
from database import get_notes, add_or_create_note, convert_notes_to_pdf, upload_image

load_dotenv()

app = FastAPI()
pinn = Pinnacle(
    api_key=os.environ["PINNACLE_API_KEY"],
)
AGENT_ID = os.environ["PINNACLE_AGENT_ID"]

get_notes_mode = {}


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
        return

    if isinstance(inbound_msg, InboundTextMessage):
        text = inbound_msg.text
        if (fromNumber in get_notes_mode) and get_notes_mode[fromNumber]:
            date = get_date(text)
            if date:
                notes = get_notes(
                    full_date=datetime.strptime(date, "%Y-%m-%d"),
                    phone_number=fromNumber,
                )
                if notes:
                    download_url = convert_notes_to_pdf(notes)
                    if download_url == None:
                        pinn.send.rcs(
                            from_=AGENT_ID,
                            to=fromNumber,
                            text="Failed to generate notes. Please try again later.",
                        )
                    else:
                        pinn.send.rcs(
                            from_=AGENT_ID,
                            to=fromNumber,
                            media_url=download_url,
                        )
                        pinn.send.rcs(
                            from_=AGENT_ID,
                            to=fromNumber,
                            **messages.get_notes_confirmation,
                        )
                else:
                    pinn.send.rcs(
                        from_=AGENT_ID, to=fromNumber, **messages.no_notes_found
                    )

                get_notes_mode[fromNumber] = False

            else:
                pinn.send.rcs(
                    from_=AGENT_ID,
                    to=fromNumber,
                    **messages.get_notes_failed_message,
                )
            return

        add_or_create_note(
            full_date=datetime.now(),
            phone_number=fromNumber,
            note={"contentType": "text", "content": text},
        )
        pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.note_added)
    elif isinstance(inbound_msg, InboundMediaMessage):
        media = inbound_msg.mediaUrls

        failed_count = 0
        for media in media:
            print(media)
            image_path = upload_image(
                datetime.now().strftime("%Y-%m-%d"),
                phone_number=fromNumber,
                image_url=media.url,
            )
            if image_path == None:
                failed_count += 1
                continue
            add_or_create_note(
                full_date=datetime.now(),
                phone_number=fromNumber,
                note={"contentType": "image", "content": image_path},
            )
        if failed_count == 0:
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.images_saved)
        else:
            pinn.send.rcs(
                from_=AGENT_ID, to=fromNumber, **messages.one_or_more_assets_failed
            )
    elif isinstance(inbound_msg, InboundActionMessage):
        action = inbound_msg.payload
        if action == "get_notes":
            get_notes_mode[fromNumber] = True
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.get_notes_message)
        elif action == "cancel":
            get_notes_mode[fromNumber] = False
            pinn.send.rcs(
                from_=AGENT_ID, to=fromNumber, **messages.get_notes_cancel_message
            )

        elif action == "summarize":
            notes = get_notes(datetime.now(), fromNumber)
            if notes == None:
                pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.no_notes_found)
                return
            summary = summarize_notes(notes)
            if summary:
                pinn.send.rcs(from_=AGENT_ID, to=fromNumber, text=summary)
                pinn.send.rcs(
                    from_=AGENT_ID, to=fromNumber, **messages.summary_finished
                )
            else:
                pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.summary_failed)
        else:
            pinn.send.rcs(from_=AGENT_ID, to=fromNumber, **messages.rcs_error_msg)
            print(f"Error message sent to {fromNumber}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("flow:app", host="0.0.0.0", port=8000, reload=True)
