from rcs import Pinnacle, SendRcsResponse
import os
from db import register_user, is_user_registered, is_user_subscribed, update_user_subscription
from rcs_utils import check_rcs_functionality
from fastapi import FastAPI, Request
import uvicorn
import os


# Retrieve the API key from an environment variable
PINNACLE_API_KEY = os.environ.get("PINNACLE_API_KEY")

# Initialize the Pinnacle RCS client with the API key from the environment
client = Pinnacle(
    api_key=PINNACLE_API_KEY,
)

app = FastAPI()

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    print(f"Received webhook data: {data}")

    if data.get('messageType') == 'message' and 'messagePayload' in data:
        payload = data['messagePayload']
        phone_number = payload.get('fromNum')
        text = payload.get('text', '').strip().lower()
        
        if phone_number:
            if text in ['yes', 'opt in', 'subscribe']:
                # User wants to opt in
                if not is_user_registered(phone_number):
                    # If not registered, register the user
                    name = "User"  # Default name, you might want to ask for the name separately
                    register_user(phone_number, name, True)
                    client.send.rcs(
                        from_="test",
                        to=phone_number,
                        text="Thank you for subscribing to Pinnacle's ArXiv AI paper notifier!"
                    )
                elif not is_user_subscribed(phone_number):
                    # If registered but not subscribed, update subscription
                    update_user_subscription(phone_number, True)
                    client.send.rcs(
                        from_="test",
                        to=phone_number,
                        text="Welcome back! You've been resubscribed to Pinnacle's ArXiv AI paper notifier."
                    )
                else:
                    # If already subscribed
                    client.send.rcs(
                        from_="test",
                        to=phone_number,
                        text="You're already subscribed to Pinnacle's ArXiv AI paper notifier."
                    )
            elif text in ['no', 'opt out', 'unsubscribe']:
                # User wants to opt out
                if is_user_subscribed(phone_number):
                    update_user_subscription(phone_number, False)
                    client.send.rcs(
                        from_="test",
                        to=phone_number,
                        text="You've been unsubscribed from Pinnacle's ArXiv AI paper notifier. We're sorry to see you go!"
                    )
                else:
                    client.send.rcs(
                        from_="test",
                        to=phone_number,
                        text="You're not currently subscribed to Pinnacle's ArXiv AI paper notifier."
                    )
    
    if data.get('messageType') == 'postback' and 'buttonPayload' in data:
        phone_number = data['buttonPayload'].get('fromNum')
        payload = data['buttonPayload'].get('payload')
        
        if payload == 'OPT_IN_YES':
            # User opted in
            print(f"User {phone_number} opted in")
            # TODO: Update user subscription status in your database
            update_user_subscription(phone_number=phone_number, is_subscribed=True)
        elif payload == 'OPT_IN_NO':
            # User opted out
            print(f"User {phone_number} opted out")
            # TODO: Handle opt-out case (e.g., remove user from database)
            update_user_subscription(phone_number=phone_number, is_subscribed=False)
    
    return {"status": "success"}


def send_optin(phone_number: str, name: str):
    is_rcs_enabled = check_rcs_functionality(phone_number)
    if not is_rcs_enabled:
        print(f"RCS not enabled on {phone_number}")
        return
    
    optin_was_sent: SendRcsResponse = client.send.rcs(
        from_ = "test",
        to = phone_number,
        text = f"Hey, {name}! Please confirm that you wish to opt into Pinnacle's ArXiv AI paper notifier",
        quick_replies = [
            {
                "title": "Yes, opt me in",
                "payload": "OPT_IN_YES",
                "type": "trigger"
            },
            {
                "title": "No, thanks",
                "payload": "OPT_IN_NO",
                "type": "trigger"
            }
        ]
    )
    print("msg:", optin_was_sent.message)

    return optin_was_sent

def opt_in(phone_number: str, name: str):
    is_registered = is_user_registered(phone_number)
    if not is_registered:
      is_sent_successfully = send_optin(phone_number, name)
      if not is_sent_successfully:
         print("Failed to sent opt-in message")
         return
      is_successful = register_user(phone_number, name, False)
      if not is_successful:
         print("Not successful")
         return
      else:
         print(f"Signed up user {phone_number}")
    is_subscribed = is_user_subscribed(phone_number)
    if not is_subscribed:
      is_sent_successfully = send_optin(phone_number, name)
      if not is_sent_successfully:
         print("Failed to sent opt-in message")
         return
      print("sent message")
    print("User is already subbed")


if __name__ == '__main__':
    opt_in("+16287261512", "Sean Roades")
    port = int(os.environ.get('PORT', default=8000))
    print("port", port)
    uvicorn.run(app, host='0.0.0.0', port=port)
    
