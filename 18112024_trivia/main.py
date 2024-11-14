from typing import Union
import anthropic
from anthropic.types.message import Message, ContentBlock
from anthropic.types.message_create_params import MessageParam
from anthropic.types.text_block import TextBlock
from dotenv import load_dotenv
import os
import json
from rcs import Action, Pinnacle, Card
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

pinnacle_api_key = os.getenv("PINNACLE_API_KEY")
if not pinnacle_api_key:
    raise ValueError("PINNACLE_API_KEY environment variable is not set")

pinnacle_client = Pinnacle(
    api_key=pinnacle_api_key,
)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("PINNACLE_API_KEY environment variable is not set")

anthropic_client = anthropic.Anthropic(
    api_key=anthropic_api_key,
)


# Define the request model
class ActionRequest(BaseModel):
    messageType: str
    actionTitle: Union[str, None] = None
    payload: Union[str, None] = None
    actionMetadata: Union[str, None] = None
    question_index: int = 0
    text: Union[str, None] = None


# Replace single variables with dictionaries keyed by phone number
trivia_data = {}  # Structure: {phone_number: current_trivia_data}
user_points = {}  # Structure: {phone_number: points}
question_indices = {}  # Structure: {phone_number: current_question_index}
difficulty_indices = {}  # Structure: {phone_number: current_difficulty_index}
asked_questions = {}  # Structure: {phone_number: [list of asked questions]}

app = FastAPI()


@app.post("/")
async def handle_action(request: ActionRequest):
    global trivia_data, user_points, question_indices, difficulty_indices, CATEGORY

    # Initialize data for new phone numbers
    if TO_NUM not in user_points:
        user_points[TO_NUM] = 0
    if TO_NUM not in question_indices:
        question_indices[TO_NUM] = 0
    if TO_NUM not in difficulty_indices:
        difficulty_indices[TO_NUM] = 0
    if TO_NUM not in asked_questions:
        asked_questions[TO_NUM] = []

    # When the app starts, send initial category selection message
    if request.messageType == "startup":
        pinnacle_client.send.rcs(
            from_="test",
            to=TO_NUM,
            cards=[
                Card(
                    title="Welcome to Trivia!",
                    subtitle="Please send a text message with your preferred category to begin.",
                )
            ],
        )
        return

    # Handle text message type
    if request.messageType == "text":
        # Reset game state for this user
        user_points[TO_NUM] = 0
        question_indices[TO_NUM] = 0
        difficulty_indices[TO_NUM] = 0
        CATEGORY = request.text or "Y Combinator"

        # Send confirmation message
        pinnacle_client.send.rcs(
            from_="test",
            to=TO_NUM,
            cards=[
                Card(
                    media_url="https://i.ibb.co/74HCVmh/Pitch-Deck-Pinnacle-12.png",
                    title=f"Category Selected: {CATEGORY}",
                    subtitle="Let's begin the trivia!",
                )
            ],
        )

        # Generate new trivia with the new category
        new_trivia = generate_trivia(
            category=CATEGORY,
            num_questions=NUM_QUESTIONS,
            difficulty=DIFFICULTIES[difficulty_indices[TO_NUM]],
        )
        if new_trivia:
            trivia(new_trivia)
        return

    if request.messageType != "action":
        raise HTTPException(status_code=400, detail="Invalid messageType")

    # Handle the action
    if request.payload == "True":
        user_points[TO_NUM] += 100
        pinnacle_client.send.rcs(
            from_="test",
            to=TO_NUM,
            cards=[
                Card(
                    title=f"Current points: {user_points[TO_NUM]}",
                    subtitle=f"You got the answer right and earned 100 points!",
                    media_url="https://i.ibb.co/vLkDHyT/Correct.png",
                )
            ],
        )
    else:
        # Check if trivia data exists before accessing
        if TO_NUM not in trivia_data or not trivia_data[TO_NUM]:
            raise HTTPException(status_code=400, detail="No trivia data available")

        # Get the current question and find the correct answer
        current_question = trivia_data[TO_NUM]["questions"][question_indices[TO_NUM]]
        correct_answer = next(
            answer["text"]
            for answer in current_question["answers"]
            if answer["correct"]
        )

        pinnacle_client.send.rcs(
            from_="test",
            to=TO_NUM,
            cards=[
                Card(
                    title=f"Current points: {user_points[TO_NUM]}",
                    subtitle=f'The correct answer was "{correct_answer}"',
                    media_url="https://i.ibb.co/4P58fYY/Incorrect.png",
                )
            ],
        )

    # Update question index handling
    question_indices[TO_NUM] += 1
    if trivia_data[TO_NUM] and question_indices[TO_NUM] < len(
        trivia_data[TO_NUM]["questions"]
    ):
        next_question = trivia_data[TO_NUM]["questions"][question_indices[TO_NUM]]
        send_question(next_question)
    else:
        # End of current difficulty level
        if difficulty_indices[TO_NUM] < len(DIFFICULTIES) - 1:
            difficulty_indices[TO_NUM] += 1
            new_trivia = generate_trivia(
                category=CATEGORY,
                num_questions=NUM_QUESTIONS,
                difficulty=DIFFICULTIES[difficulty_indices[TO_NUM]],
            )
            if new_trivia:
                pinnacle_client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[
                        Card(
                            title=f"{DIFFICULTIES[difficulty_indices[TO_NUM] - 1].title()} Level Complete!",
                            subtitle=f"Moving To {DIFFICULTIES[difficulty_indices[TO_NUM]].title()} Difficulty.",
                        )
                    ],
                )
                trivia(new_trivia)
        else:
            # End of all difficulty levels
            pinnacle_client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title=f"Final score: {user_points[TO_NUM]}",
                        subtitle=f"Congratulations, you've completed all difficulty levels!",
                        media_url="https://i.ibb.co/444L50Z/congrats.png",
                    )
                ],
            )
            pinnacle_client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        media_url="https://i.ibb.co/74HCVmh/Pitch-Deck-Pinnacle-12.png",
                        title="Welcome to Trivia!",
                        subtitle="""Please send a text message with your preferred category to begin, e.g., "Y Combinator", "Call of Duty Zombies", "Dolphins", etc.""",
                    )
                ],
            )


DIFFICULTIES_IMAGES = {
    "easy": "https://i.ibb.co/0DdLWGY/easy.png",
    "medium": "https://i.ibb.co/3yVPns8/medium.png",
    "hard": "https://i.ibb.co/X3ddvjG/hard.png",
    "very hard": "https://i.ibb.co/TcSv4pB/very-hard.png",
    "extremely hard": "https://i.ibb.co/4SgxL5d/Extremeley-hard-round.png",
    "impossible": "https://i.ibb.co/B23tkkL/Impossible-round.png",
}


def send_question(q):
    """Helper function to send a single trivia question"""
    current_difficulty = DIFFICULTIES[difficulty_indices[TO_NUM]]
    pinnacle_client.send.rcs(
        from_="test",
        to=TO_NUM,
        cards=[
            Card(
                title=q["question"],
                subtitle=q["subtitle"],
                media_url=DIFFICULTIES_IMAGES[current_difficulty],
            )
        ],
        quick_replies=[
            Action(
                type="trigger",
                title=answer["text"],
                payload=str(answer["correct"]),
            )
            for answer in q["answers"]
        ],
    )


def generate_trivia(
    category: str, num_questions: int, difficulty: str
) -> Union[str, None]:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            message: Message = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                temperature=0.5,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""You are tasked with generating a set of trivia questions based on a specified category. Your goal is to create engaging and diverse questions with multiple-choice answers in a structured JSON format.

        You will be provided with these inputs:
        <category>
        {category}
        </category>
        This is the category for which you should generate trivia questions.

        <num_questions>
        {num_questions}
        </num_questions>
        This is the number of questions you should generate. If not specified, generate 5 questions.

        <difficulty>
        {difficulty}
        </difficulty>
        This is the difficulty of questions you should generate. If not specified, generate questions of medium difficulty.

        <previously_asked_questions>
        {asked_questions}
        </previously_asked_questions>
        These questions have already been asked. Do not repeat any of these questions.

        Follow these steps to generate the trivia questions:

        1. Based on the given category, brainstorm interesting and diverse topics within that category.
        2. For each topic, create a question that tests knowledge related to that topic.
        3. Generate a brief subtitle for each question that provides context or additional information.
        4. Create four multiple-choice answers for each question, ensuring that only one is correct.
        5. Arrange the questions, subtitles, and answers in the required JSON format.

        The output should be in the following JSON format:

        ```json
        {{
        "category": "Category Name",
        "questions": [
            {{
            "question": "Question text goes here?",
            "subtitle": "Brief subtitle or context for the question",
            "answers": [
                {{"text": "Correct answer", "correct": true}},
                {{"text": "Incorrect answer 1", "correct": false}},
                {{"text": "Incorrect answer 2", "correct": false}},
                {{"text": "Incorrect answer 3", "correct": false}}
            ]
            }},
            {{
            // Additional questions follow the same structure
            }}
        ]
        }}
        ```

        Here's an example of how a single question should be structured within the JSON:

        ```json
        {{
        "question": "Which planet is known as the 'Red Planet'?",
        "subtitle": "This planet's reddish appearance is due to iron oxide on its surface",
        "answers": [
            {{"text": "Mars", "correct": true}},
            {{"text": "Venus", "correct": false}},
            {{"text": "Jupiter", "correct": false}},
            {{"text": "Saturn", "correct": false}}
        ]
        }}
        ```

        Additional guidelines:
        - Ensure that questions are factually accurate and appropriate for the given category.
        - Vary the difficulty level of questions to maintain interest.
        - Avoid repetitive or overly similar questions.
        - Make sure that the correct answer is not always in the same position.
        - Double-check that there is only one correct answer per question.
        - Answers must be less than 25 characters.

        Begin generating the trivia questions based on the provided category and number of questions. Present your output in valid JSON format, starting with an opening curly brace {{ and ending with a closing curly brace }}.""",
                            }
                        ],
                    }
                ],
            )
            text = (
                message.content[0].text
                if isinstance(message.content[0], TextBlock)
                else None
            )

            if not text:
                print(f"No text received on attempt {attempt + 1}, retrying...")
                continue

            # Try to parse JSON, if it fails, try again
            try:
                json.loads(text)  # Test if valid JSON
                return text
            except json.JSONDecodeError:
                print(f"Invalid JSON received on attempt {attempt + 1}, retrying...")
                continue

        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                print(
                    f"Failed to generate trivia after {max_retries} attempts: {str(e)}"
                )
                return None
            print(f"Attempt {attempt + 1} failed, retrying...")
            continue

    return None


TO_NUM = "+16287261512"


def trivia(text: str):
    """Start trivia from claude's generated trivia."""
    global trivia_data, question_indices, asked_questions
    try:
        trivia_data[TO_NUM] = json.loads(text)
        question_indices[TO_NUM] = 0

        if trivia_data[TO_NUM]["questions"]:
            # Add new questions to asked_questions list
            if TO_NUM not in asked_questions:
                asked_questions[TO_NUM] = []
            for question in trivia_data[TO_NUM]["questions"]:
                asked_questions[TO_NUM].append(question["question"])
            send_question(trivia_data[TO_NUM]["questions"][0])

    except json.JSONDecodeError:
        print("Failed to parse JSON response")


CATEGORY = "Our planet 2"
NUM_QUESTIONS = 1
DIFFICULTIES = ["easy", "medium", "hard", "very hard", "extremely hard", "impossible"]


def main() -> None:
    # Send initial category selection message
    pinnacle_client.send.rcs(
        from_="test",
        to=TO_NUM,
        cards=[
            Card(
                media_url="https://i.ibb.co/74HCVmh/Pitch-Deck-Pinnacle-12.png",
                title="Welcome to Trivia!",
                subtitle="""Please send a text message with your preferred category to begin, e.g., "Y Combinator", "Call of Duty Zombies", "Dolphins", etc.""",
            )
        ],
    )

    # Start the FastAPI server
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
