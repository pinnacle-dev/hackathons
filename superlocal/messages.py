from rcs import Action, Card
from rcs_types import RCSMessage

search_actions_dict = {
    "parks": {"title": "Parks 🌳", "media_url": "https://i.ibb.co/GTKTQbL/park.webp"},
    "parking": {
        "title": "Parking 🚗",
        "media_url": "https://i.ibb.co/sVLBPT8/parking.webp",
    },
    "fun_activities": {
        "title": "Fun Activities 🎉",
        "media_url": "https://i.ibb.co/X3CR3Cq/fun-activites.webp",
    },
    "cafes": {
        "title": "Cafes with WiFi 🛜",
        "media_url": "https://i.ibb.co/JKr4KxS/cafes.webp",
    },
    "restaurants": {
        "title": "Restaurants 🍔",
        "media_url": "https://i.ibb.co/dKgmLpP/restaurants.webp",
    },
    "restrooms": {
        "title": "Restrooms 🚽",
        "media_url": "https://i.ibb.co/k45QW9B/restroom.webp",
    },
}

search_actions = [
    Action(title=payloadValue["title"], type="trigger", payload=payload)
    for payload, payloadValue in search_actions_dict.items()
]

rcs_error_msg: RCSMessage = {
    "text": "Sorry, I didn't understand that. What are you looking for?",
    "quick_replies": search_actions,
}

waiting_msg: RCSMessage = {
    "cards": [
        Card(
            title="Waiting on your location 📍",
            media_url="https://i.ibb.co/ZW7fJQZ/waiting.webp",
        )
    ]
}


intro_msg: RCSMessage = {
    "text": "I'm Rocket 🚀 and I'm here to sniff out the best spots near you. What can I help you find?",
    "quick_replies": search_actions,
}


def create_request_location_msg(payloadValue: str) -> RCSMessage:

    if payloadValue not in search_actions_dict:
        return rcs_error_msg

    return {
        "cards": [
            Card(
                title="Looking for " + search_actions_dict[payloadValue]["title"],
                subtitle="Click the button below to share your location with me.",
                media_url=search_actions_dict[payloadValue]["media_url"],
                buttons=[
                    Action(
                        title="Share Location 📍",
                        type="requestUserLocation",
                    )
                ],
            )
        ]
    }
