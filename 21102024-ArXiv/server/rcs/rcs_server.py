import logging
from fastapi import FastAPI, HTTPException, Request
import uvicorn
import httpx
import json
from dotenv import load_dotenv
import os
import sys
from pydantic import TypeAdapter
from rcs_types import InboundMessage

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from arxiv import send_functions


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        return json.dumps(log_record)


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

load_dotenv()

app = FastAPI()

RCS_URL = os.environ["RCS_URL"]  # Set to dev / prod via this


@app.get("/")
async def welcome():
    return {"message": "Welcome to the Pinnacle API"}


@app.post("/")
async def receive_message(request: Request):
    # Log the raw request json
    json_data = await request.json()
    logger.info(f"Received raw json: {json_data}")
    print(f"Received raw json: {json_data}")  # Added print statement
    if (
        request.headers.get("pinnacle-signing-secret")
        != os.environ["PINNACLE_SIGNING_SECRET"]
    ):
        print("Invalid signing secret")
        return

    try:
        inbound_msg = TypeAdapter(InboundMessage).validate_python(json_data)
        print(inbound_msg)
    except Exception as e:
        logger.error(f"Error validating inbound message: {str(e)}")
        print(f"Error validating inbound message: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON data")

    # Validate the message type
    if inbound_msg.messageType != "text" and inbound_msg.messageType != "action":
        logger.error(f"Invalid message type: {inbound_msg.messageType}")
        print(
            f"Invalid message type: {inbound_msg.messageType}"
        )  # Added print statement
        raise HTTPException(status_code=400, detail="Invalid message type")

    # Handle the message based on its type
    if inbound_msg.messageType == "text":
        logger.info(f"Received message from {inbound_msg.from_}: {inbound_msg.text}")
        print(
            f"Received message from {inbound_msg.from_}: {inbound_msg.text}"
        )  # Added print statement
    else:  # postback
        logger.info(
            f"Received postback from {inbound_msg.from_}: {inbound_msg.actionTitle} (Payload: {inbound_msg.payload})"
        )
        print(
            f"Received postback from {inbound_msg.from_}: {inbound_msg.actionTitle} (Payload: {inbound_msg.payload})"
        )  # Added print statement

    # Forward the message to the RCS listener
    async with httpx.AsyncClient() as client:
        try:
            # Update the RCS_URL to include the full path
            logger.info(f"Attempting to forward message to: {RCS_URL}")

            # Map the from_ field to from
            if (
                inbound_msg.messageType == "action"
                and (inbound_msg.payload)
                and (
                    inbound_msg.payload in ["ABOUT", "SEE_MORE"]
                    or inbound_msg.payload.startswith("PAPER_")
                )
            ):
                if inbound_msg.payload == "ABOUT":
                    send_functions.sendAboutProject(inbound_msg.from_)
                elif inbound_msg.payload == "SEE_MORE":
                    send_functions.sendPopularPapers(inbound_msg.from_)
                elif inbound_msg.payload.startswith("PAPER_"):
                    send_functions.sendAboutPaper(
                        inbound_msg.from_, inbound_msg.payload.replace("PAPER_", "")
                    )
            else:
                inbound_msg_dict = inbound_msg.model_dump()
                inbound_msg_dict["from"] = inbound_msg_dict.pop("from_")

                response = await client.post(url=RCS_URL, json=inbound_msg_dict)
                response.raise_for_status()

                logger.info(
                    f"Message successfully forwarded to RCS listener. Status code: {response.status_code}"
                )
                return {
                    "status": "Message received and forwarded to RCS listener",
                    "rcs_response": response.text,
                }
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error forwarding message to RCS listener: {e.response.status_code} - {e.response.text}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error forwarding message to RCS listener: {e.response.status_code} - {e.response.text}",
            )
        except httpx.RequestError as e:
            logger.error(f"Request error forwarding message to RCS listener: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Request error forwarding message to RCS listener: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting RCS server. Press Ctrl+C to stop.")
    uvicorn.run("rcs_server:app", host="0.0.0.0", port=8000, reload=True)
