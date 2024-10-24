import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
import httpx
from datetime import datetime
from typing import Union
import json
from dotenv import load_dotenv
import os
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
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

class MessagePayload(BaseModel):
    mediaType: str
    media: str
    text: str
    sent: datetime
    fromNum: str

class ButtonPayload(BaseModel):
    title: str
    payload: str
    execute: str
    sent: datetime
    fromNum: str

class Message(BaseModel):
    messageType: str
    messagePayload: Union[MessagePayload, ButtonPayload]

RCS_URL = os.getenv("RCS_URL") # Set to dev / prod via this

@app.post("/")
async def receive_message(request: Request):
    # Log the raw request body
    body = await request.body()
    logger.info(f"Received raw body: {body.decode()}")

    # Parse the JSON data
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON data received")
        raise HTTPException(status_code=400, detail="Invalid JSON data")

    # Validate the message type
    if data["messageType"] not in ["message", "postback"]:
        logger.error(f"Invalid message type: {data['messageType']}")
        raise HTTPException(status_code=400, detail="Invalid message type")
    
    # Handle the message based on its type
    if data["messageType"] == "message":
        payload = data["messagePayload"]
        logger.info(f"Received message from {payload['fromNum']}: {payload['text']}")
    else:  # postback
        payload = data["buttonPayload"]
        logger.info(f"Received postback from {payload['fromNum']}: {payload['title']} (Payload: {payload['payload']})")
    
    # Forward the message to the RCS listener
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=RCS_URL, json=data)
            response.raise_for_status()
            logger.info("Message successfully forwarded to RCS listener")
            return {"status": "Message received and forwarded to RCS listener"}
        except httpx.HTTPStatusError as e:
            logger.error(f"Error forwarding message to RCS listener: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error forwarding message to RCS listener: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting RCS server. Press Ctrl+C to stop.")
    uvicorn.run("rcs_server:app", host="0.0.0.0", port=8000, reload=True)
