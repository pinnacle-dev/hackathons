from rcs import Action
from rcs_types import RCSMessage
from typing import List
import random

restart_action = Action(
    title="Restart",
    type="trigger",
    payload="restart",
)

get_wifi_action = Action(
    title="Get WiFi",
    type="trigger",
    payload="get_wifi",
)


share_wifi_action = Action(
    title="Share WiFi",
    type="trigger",
    payload="share_wifi",
)

lock_door_action = Action(
    title="Lock Door",
    type="trigger",
    payload="lock_door",
)

unlock_door_action = Action(
    title="Unlock Door",
    type="trigger",
    payload="unlock_door",
)

base_actions = [
    get_wifi_action,
    share_wifi_action,
    unlock_door_action,
    lock_door_action,
]

rcs_error_msg: RCSMessage = {
    "text": "Sorry, I didn't understand that. Please try again.",
    "quick_replies": base_actions,
}


intro_msg: RCSMessage = {
    "text": "Welcome to the Pinnacle Penthouse! I'm Rocket 🚀. How can I help you today?",
    "quick_replies": base_actions,
}


wifi_msg: RCSMessage = {
    "media_url": "https://i.ibb.co/CnXB6tc/pinnacle-wifi.png",
    "quick_replies": base_actions,
}


combination_codes = [
    "🦝🚀△",
    "👀🤖💩",
    "🌟🔥💧",
    "🎉🎈🍰",
    "🚀🌕⭐",
    "🍕🍔🍟",
    "🎸🎤🎵",
]


def create_combinations(door_action: str) -> List[Action]:
    return [
        Action(title=code, type="trigger", payload=door_action, metadata=code)
        for _, code in enumerate(
            random.sample(combination_codes, len(combination_codes))
        )
    ] + [restart_action]
