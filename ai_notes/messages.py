from rcs import Action
from rcs_types import RCSMessage

summarize_notes_action = Action(
    title="Summarize Notes",
    type="trigger",
    payload="summarize",
)


get_notes_action = Action(
    title="Get Notes",
    type="trigger",
    payload="get_notes",
)

base_actions = [
    summarize_notes_action,
    get_notes_action,
]

rcs_error_msg: RCSMessage = {
    "text": "Sorry, I was unable to add your notes. Please try sending the message again or select another action.",
    "quick_replies": base_actions,
}

note_added: RCSMessage = {
    "text": "Note added successfully! Select an action or add another note to continue.",
    "quick_replies": base_actions,
}

images_saved: RCSMessage = {
    "text": "Image(s) saved successfully! Select an action or add another note to continue.",
    "quick_replies": base_actions,
}

one_or_more_assets_failed: RCSMessage = {
    "text": "Some images were not saved. We currently only support saving images. Please try again.",
    "quick_replies": base_actions,
}

get_notes_message: RCSMessage = {
    "text": "When did you want to see your notes from? Text a date or something like 'last week' or 'yesterday'.",
    "quick_replies": [
        Action(
            title="Cancel",
            type="trigger",
            payload="cancel",
        ),
    ],
}

get_notes_confirmation: RCSMessage = {
    "text": "Here are your notes! Text us to add more notes or select another action.",
    "quick_replies": base_actions,
}

get_notes_failed_message: RCSMessage = {
    "text": "Sorry, I was unable to find any notes for that date. Try again by texting a date or something like 'last week' or 'yesterday'.",
    "quick_replies": [
        Action(
            title="Cancel",
            type="trigger",
            payload="cancel",
        ),
    ],
}

get_notes_cancel_message: RCSMessage = {
    "text": "Okay, I won't show you your notes. Select an action or text another note to continue.",
    "quick_replies": base_actions,
}

no_notes_found: RCSMessage = {
    "text": "No notes found! Add a note for today by texting us now.",
    "quick_replies": base_actions,
}

summary_failed: RCSMessage = {
    "text": "Sorry, I was unable to summarize your notes. Please try again later.",
    "quick_replies": base_actions,
}

summary_finished: RCSMessage = {
    "text": "And thats it! Select an action or add another note by texting us.",
    "quick_replies": [get_notes_action],
}
