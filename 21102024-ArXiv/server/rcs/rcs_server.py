from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
import httpx
from datetime import datetime
from typing import Union
import json

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

@app.post("/")
async def receive_message(request: Request):
    # Log the raw request body
    body = await request.body()
    print(f"Received raw body: {body.decode()}")

    # Parse the JSON data
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")

    # Validate the message type
    if data["messageType"] not in ["message", "postback"]:
        raise HTTPException(status_code=400, detail="Invalid message type")
    
    # Handle the message based on its type
    if data["messageType"] == "message":
        payload = data["messagePayload"]
        print(f"Received message from {payload['fromNum']}: {payload['text']}")
    else:  # postback
        payload = data["buttonPayload"]
        print(f"Received postback from {payload['fromNum']}: {payload['title']} (Payload: {payload['payload']})")
    
    # Forward the message to the RCS listener
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://localhost:3000/api/rcs_listener", json=data)
            response.raise_for_status()
            return {"status": "Message received and forwarded to RCS listener"}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=f"Error forwarding message to RCS listener: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    print("Starting RCS server. Press Ctrl+C to stop.")
    uvicorn.run("rcs_server:app", host="0.0.0.0", port=8000, reload=True)
