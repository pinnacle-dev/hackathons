from time import sleep
from typing import Dict, Callable

from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import random

from health_bar import overlay_health_bars
from rcs import Action, Card, Pinnacle, SendRcsResponse
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

KEY: str | None = os.getenv("PINNACLE_API_KEY")
if not KEY:
    raise ValueError("No key provided")

client = Pinnacle(
    api_key=KEY,
)

class ActionMessage(BaseModel):
    messageType: str
    actionTitle: str
    payload: str | None = None
    actionMetadata: str | None = None

TO_NUM = "+16287261512"
BACKGROUND_IMAGE_PATH = "./battle_bg.png"
ATTACK_IMAGE_PATH = "./AttackingState.png"

def pause() -> None:
    sleep(3)
    client.send.rcs(
        from_="test",
        to=TO_NUM,
        text="..."
    )
    sleep(1)

def attack_menu(image_url: str) -> None:
    client.send.rcs(
        from_="test",
        to=TO_NUM,
        cards=[
            Card(
                media_url=image_url,
                title="Choose your attack!",
                subtitle="Select one of Pikachu's moves"
            )
        ],
        quick_replies=[
            Action(
                title=f"Thunderbolt (90)",
                type="trigger",
                payload="THUNDERBOLT",
            ),
            Action(
                title=f"Quick Attack (40)",
                type="trigger",
                payload="QUICK_ATTACK",
            ),
            Action(
                title=f"Iron Tail (100)",
                type="trigger",
                payload="IRON_TAIL",
            ),
            Action(
                title=f"Volt Tackle (120)",
                type="trigger",
                payload="VOLT_TACKLE",
            ),
            Action(
                title=f"Throw Pokéball",
                type="trigger",
                payload="CAPTURE",
            ),
        ]
    )

def init_battle() -> str:
    init_response: SendRcsResponse = client.send.rcs(
        from_="test",
        to=TO_NUM,
        cards=[
            Card(
                media_url="https://www.dropbox.com/scl/fi/zgw0rn2qua113l00bfupt/Pokemon.mp4?rlkey=tjglm3c1ttcoidmamujopz9yc&st=k5gvk2qu&raw=1",
                title="A Wild Zigzagoon Appears!",
            )
        ],
    )

    pause()

    image_url: str = overlay_health_bars(
        background_image_path=BACKGROUND_IMAGE_PATH,
        enemy_health=100,
        enemy_max_health=100,
        user_health=100,
        user_max_health=100,
        upload=True
    )

    battle_response: SendRcsResponse = client.send.rcs(
        from_="test",
        to=TO_NUM,
        cards=[
            Card(
                media_url=image_url,
                title="What will you do?",
            )
        ],
        quick_replies=[
            Action(
                title="Fight",
                type="trigger",
                payload="FIGHT",
            ),
            Action(
                title="Capture",
                type="trigger",
                payload="CAPTURE",
            ),
        ]
    )

    return battle_response.message

class Pikachu:
    def __init__(self):
        self.max_health = 186
        self.current_health = self.max_health
        self.defense = 100
        
    def thunderbolt(self) -> int:
        """High-power electric attack"""
        if random.randint(1, 8) == 1:  # 1 in 8 chance to miss (higher chance for high damage)
            return 0  # Attack missed
        base_damage = 90
        if random.randint(1, 16) == 1:
            return int(base_damage * 1.5)
        return int(base_damage)
    
    def quick_attack(self) -> int:
        """Fast physical attack that always hits first"""
        if random.randint(1, 16) == 1:  # 1 in 16 chance to miss (lower chance)
            return 0  # Attack missed
        base_damage = 40
        if random.randint(1, 16) == 1:
            return int(base_damage * 1.5)
        return int(base_damage)
    
    def iron_tail(self) -> int:
        """Strong physical attack with chance to lower defense"""
        if random.randint(1, 8) == 1:
            return 0  
        base_damage = 100
        if random.randint(1, 16) == 1:
            return int(base_damage * 1.5)
        return int(base_damage)
    
    def volt_tackle(self) -> tuple[int, int]:
        """Powerful electric attack that also damages the user"""
        if random.randint(1, 16) == 1:
            return 0, 0  # Attack missed
        base_damage = 120
        if random.randint(1, 16) == 1:
            damage = int(base_damage * 1.5)
        else:
            damage = int(base_damage)
        recoil = int(damage * 0.33)  # 33% recoil damage
        return damage, recoil
    
    def calculate_damage(self, base_damage: int) -> int:
        """Calculate actual damage taking defense into account"""
        defense_multiplier = 100 / self.defense  # Lower defense = higher multiplier
        return int(base_damage * defense_multiplier)
    
class Zigzagoon:
    def __init__(self):
        self.max_health = 280
        self.current_health = self.max_health
        self.defense = 100  # Base defense value of 100%
        
    def tackle(self) -> int:
        """Basic physical attack"""
        if random.randint(1, 16) == 1:  # 1 in 16 chance to miss (lower chance)
            return 0  # Attack missed
        base_damage = 40
        if random.randint(1, 16) == 1:
            return int(base_damage * 1.5)
        return int(base_damage)
    
    def headbutt(self) -> int:
        """Stronger physical attack with chance to flinch"""
        if random.randint(1, 12) == 1:  # 1 in 12 chance to miss (medium chance)
            return 0  # Attack missed
        base_damage = 70
        if random.randint(1, 16) == 1:
            return int(base_damage * 1.5)
        return int(base_damage)
    
    def pin_missile(self) -> int:
        """Hits 2-5 times in succession"""
        if random.randint(1, 16) == 1:  # 1 in 16 chance to miss (lower chance)
            return 0  # Attack missed
        base_damage = 25  # Per hit
        if random.randint(1, 16) == 1:
            return int(base_damage * 1.5)
        return int(base_damage)
    
    def tail_whip(self, target: 'Pikachu') -> int:
        """Lowers opponent's defense"""
        target.defense = max(50, target.defense - 20)
        return 0
        
    def calculate_damage(self, base_damage: int) -> int:
        """Calculate actual damage taking defense into account"""
        defense_multiplier = 100 / self.defense 
        return int(base_damage * defense_multiplier)

pikachu = Pikachu()
zigzagoon = Zigzagoon()

DODGE_VIDEO_PATH = "https://www.dropbox.com/scl/fi/xwwsverdorfqwjetcwe17/dodgewsound.mov?rlkey=3cavfh8o75ud18czkhbukgrzb&st=5ma9bkp4&raw=1"
THUNDERBOLT_VIDEO_PATH = "https://www.dropbox.com/scl/fi/o2ygkv5gmhzwbd51r7zac/thunderbolt.m4v?rlkey=1ozafhmmtdkinipim5p44f96w&st=t33isn6v&raw=1"
QUICK_ATTACK_VIDEO_PATH = "https://www.dropbox.com/scl/fi/mmsad9wy66fzvdxbx9xwf/quickAttack.mp4?rlkey=6ay3cwkbuf3l689ky6ikoxou8&st=owsq0e74&raw=1"
IRON_TAIL_VIDEO_PATH = "https://www.dropbox.com/scl/fi/yasbhrivod61t8997x2xo/Shiny-Glow.mp4?rlkey=9bwcetvw9v81wuscs5df8dgpq&st=s4krpwvg&raw=1"
VOLT_TACKLE_VIDEO_PATH = "https://www.dropbox.com/scl/fi/o2ygkv5gmhzwbd51r7zac/thunderbolt.m4v?rlkey=1ozafhmmtdkinipim5p44f96w&st=t33isn6v&raw=1"
ATTACK_IMAGE_URL = "https://i.ibb.co/c2RrFDx/fainted.png"
PIKA_FAINTED_URL = "https://i.ibb.co/b3XgcZY/Faintedpika.png"
THROW_BALL_VIDEO_URL = "https://www.dropbox.com/scl/fi/va5io9m8w2duvkxa5b308/Video-Capture.mp4?rlkey=s7zjq4gk8e5zrsc92wk11kdrc&st=2q8r3e2p&raw=1"
BREAK_FREE_URL = "https://www.dropbox.com/scl/fi/73ugaryplc530jkadr2fy/break_free.mp4?rlkey=o8vl1puvkg9os2ykjjb7qy3ng&st=29pjcwef&raw=1"
SHAKE_BALL_URL = "https://www.dropbox.com/scl/fi/nhqdmol208onzojrish5w/shake_ball.mp4?rlkey=sn0s9yw0u77gm5gpmvsz1bcx6&st=4086qje2&raw=1"
ZIGZAGOON_CAPTURED_URL = "https://i.ibb.co/Y8nmkrg/captured.png"


def perform_zigzagoon_attack(health_bar_image_url: str) -> bool:
    """
    Performs Zigzagoon's attack turn and returns True if battle should continue
    """
    # Define attacks list with tuples of (function, name)
    zigzagoon_attacks = [
        (zigzagoon.tackle, "tackle"),
        (zigzagoon.headbutt, "headbutt"),
        (zigzagoon.pin_missile, "pin_missile"),
        (lambda: zigzagoon.tail_whip(pikachu), "tail_whip")
    ]

    # Choose random attack using index
    attack_index = random.randint(0, len(zigzagoon_attacks) - 1)
    attack_func, attack_name = zigzagoon_attacks[attack_index]
    
    damage = attack_func()  # Execute the chosen attack
    
    if damage == 0:
        if attack_func == zigzagoon.tail_whip:
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[Card(
                    media_url=health_bar_image_url,
                    title="Zigzagoon used Tail Whip!",
                    subtitle="Pikachu's defense was lowered."
                )]
            )
        else:
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[Card(
                    media_url=health_bar_image_url,
                    title=f"Zigzagoon used {attack_name.replace('_', ' ').title()}!",
                    subtitle="The attack missed!"
                )]
            )
        return True
        
    pikachu.current_health -= damage
    
    # Check if Pikachu fainted
    if pikachu.current_health <= 0:
        client.send.rcs(
            from_="test",
            to=TO_NUM,
            cards=[Card(
                media_url=PIKA_FAINTED_URL,
                title="Pikachu fainted!",
                subtitle="You blacked out!"
            )]
        )
        return False
        
    updated_health_bar_image_url: str = overlay_health_bars(
        background_image_path=ATTACK_IMAGE_PATH,
        enemy_health=zigzagoon.current_health,
        enemy_max_health=zigzagoon.max_health,
        user_health=pikachu.current_health,
        user_max_health=pikachu.max_health,
        upload=True
    )
    
    client.send.rcs(
        from_="test",
        to=TO_NUM,
        cards=[Card(
            media_url=updated_health_bar_image_url,
            title=f"Zigzagoon used {attack_name.replace('_', ' ').title()}!",
            subtitle=f"Pikachu took {damage} damage."
        )]
    )
    return True

def finish_turn() -> None:
    # Check if Zigzagoon fainted from the previous attack
    if zigzagoon.current_health <= 0:
        client.send.rcs(
            from_="test",
            to=TO_NUM,
            cards=[Card(
                media_url=ATTACK_IMAGE_URL,
                title="Victory!",
                subtitle="The wild Zigzagoon fainted! You won the battle!"
            )]
        )
        return
    
    health_bar_image_url: str = overlay_health_bars(
        background_image_path=ATTACK_IMAGE_PATH,
        enemy_health=max(0, zigzagoon.current_health),
        enemy_max_health=zigzagoon.max_health,
        user_health=max(0, pikachu.current_health),
        user_max_health=pikachu.max_health,
        upload=True
    )
    
    pause()
    
    # Perform Zigzagoon's attack
    battle_continues = perform_zigzagoon_attack(health_bar_image_url)
    if not battle_continues:
        return
        
    pause()

    updated_health_bar_image_url2: str = overlay_health_bars(
        background_image_path=ATTACK_IMAGE_PATH,
        enemy_health=zigzagoon.current_health,
        enemy_max_health=zigzagoon.max_health,
        user_health=pikachu.current_health,
        user_max_health=pikachu.max_health,
        upload=True
    )
    
    # Only show attack menu if battle is still ongoing
    if pikachu.current_health > 0 and zigzagoon.current_health > 0:
        attack_menu(image_url=updated_health_bar_image_url2)

    
@app.post("/")
async def webhook(message: ActionMessage) -> Dict[str, str]:
    global pikachu, zigzagoon

    if isinstance(message, ActionMessage):
        match message.payload:
            case "FIGHT":
                image_url: str = overlay_health_bars(
                    background_image_path=ATTACK_IMAGE_PATH,
                    enemy_health=zigzagoon.current_health,
                    enemy_max_health=zigzagoon.max_health,
                    user_health=pikachu.current_health,
                    user_max_health=pikachu.max_health,
                    upload=True
                )
                fight_response: SendRcsResponse = client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[
                        Card(
                            media_url=image_url,
                            title="Choose your attack!",
                            subtitle="Select one of Pikachu's moves"
                        )
                    ],
                    quick_replies=[
                        Action(
                            title=f"Thunderbolt (90)",
                            type="trigger",
                            payload="THUNDERBOLT",
                        ),
                        Action(
                            title=f"Quick Attack (40)",
                            type="trigger",
                            payload="QUICK_ATTACK",
                        ),
                        Action(
                            title=f"Iron Tail (100)",
                            type="trigger",
                            payload="IRON_TAIL",
                        ),
                        Action(
                            title=f"Volt Tackle (120)",
                            type="trigger",
                            payload="VOLT_TACKLE",
                        ),
                    ]
                )
                return {"status": "ok", "message": fight_response.message}
            
            case "THUNDERBOLT":
                print("THUNDERBOLT", THUNDERBOLT_VIDEO_PATH)
                damage = pikachu.thunderbolt()
                if damage == 0:
                    client.send.rcs(
                        from_="test",
                        to=TO_NUM,
                        cards=[
                            Card(
                                media_url=DODGE_VIDEO_PATH,
                                title="Pikachu's Attack Missed!",
                                subtitle="Zigzagoon dodged the attack."
                            )
                        ]
                    )
                    return {"status": "ok", "message": "Pikachu's Attack Missed!"}
                
                zigzagoon.current_health -= damage
                res = client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[
                        Card(
                            media_url=THUNDERBOLT_VIDEO_PATH,
                            title="Pikachu used Thunderbolt!",
                            subtitle=f"Zigzagoon took {damage} damage."
                        )
                    ]
                )
                print(res)
                finish_turn()
                return {"status": "ok", "message": f"Pikachu used Thunderbolt! Zigzagoon took {damage} damage."}

            case "QUICK_ATTACK":
                print("QUICK_ATTACK")
                damage = pikachu.quick_attack()
                if damage == 0:
                    client.send.rcs(
                        from_="test",
                        to=TO_NUM,
                        cards=[
                            Card(
                                media_url=DODGE_VIDEO_PATH,
                                title="Pikachu's Attack Missed!",
                                subtitle="Zigzagoon dodged the attack."
                            )
                        ]
                    )
                    return {"status": "ok", "message": "Pikachu's Attack Missed!"}
                
                zigzagoon.current_health -= damage
                res = client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[
                        Card(
                            media_url=QUICK_ATTACK_VIDEO_PATH,
                            title="Pikachu used Quick Attack!",
                            subtitle=f"Zigzagoon took {damage} damage."
                        )
                    ]
                )
                print(res)
                finish_turn()
                return {"status": "ok", "message": f"Pikachu used Quick Attack! Zigzagoon took {damage} damage."}

            case "IRON_TAIL":
                print("IRON_TAIL")
                damage = pikachu.iron_tail()
                if damage == 0:
                    client.send.rcs(
                        from_="test",
                        to=TO_NUM,
                        cards=[
                            Card(
                                media_url=DODGE_VIDEO_PATH,
                                title="Pikachu's Attack Missed!",
                                subtitle="Zigzagoon dodged the attack."
                            )
                        ]
                    )
                    return {"status": "ok", "message": "Pikachu's Attack Missed!"}
                
                zigzagoon.current_health -= damage
                res = client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[
                        Card(
                            media_url=IRON_TAIL_VIDEO_PATH,
                            title="Pikachu used Iron Tail!",
                            subtitle=f"Zigzagoon took {damage} damage."
                        )
                    ]
                )
                print(res)
                finish_turn()
                return {"status": "ok", "message": f"Pikachu used Iron Tail! Zigzagoon took {damage} damage."}

            case "VOLT_TACKLE": 
                print("VOLT_TACKLE")
                damage, recoil = pikachu.volt_tackle()
                if damage == 0:
                    client.send.rcs(
                        from_="test",
                        to=TO_NUM,
                        cards=[
                            Card(
                                media_url=DODGE_VIDEO_PATH,
                                title="Pikachu's Attack Missed!",
                                subtitle="Zigzagoon dodged the attack."
                            )
                        ]
                    )
                    return {"status": "ok", "message": "Pikachu's Attack Missed!"}
                
                zigzagoon.current_health -= damage
                pikachu.current_health -= recoil
                res = client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[
                        Card(
                            media_url=VOLT_TACKLE_VIDEO_PATH,
                            title="Pikachu used Volt Tackle!",
                            subtitle=f"Zigzagoon took {damage} damage and Pikachu took {recoil} recoil damage."
                        )
                    ]
                )
                print(res)
                finish_turn()
                return {"status": "ok", "message": f"Pikachu used Volt Tackle! Zigzagoon took {damage} damage and Pikachu took {recoil} recoil damage."}
            
            case "CAPTURE":
                client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[Card(
                        media_url=THROW_BALL_VIDEO_URL,
                        title="You threw a Pokéball!",
                    )]
                )

                pause()
                                
                # Calculate break-free probability based on health percentage
                health_percentage = (zigzagoon.current_health / zigzagoon.max_health) * 100
                
                # First shake
                if (health_percentage >= 90 and random.random() < 2/3) or \
                   (30 <= health_percentage < 90 and random.random() < 1/3) or \
                   (health_percentage < 30 and random.random() < 0.1):
                    client.send.rcs(
                        from_="test",
                        to=TO_NUM,
                        cards=[Card(media_url=BREAK_FREE_URL, title="Oh no! The Pokémon broke free!")]
                    )
                    finish_turn()
                    return {"status": "ok"}

                client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[Card(media_url=SHAKE_BALL_URL, title="...")]
                )

                pause()

                # Second shake
                if (health_percentage >= 90 and random.random() < 2/3) or \
                   (30 <= health_percentage < 90 and random.random() < 1/3) or \
                   (health_percentage < 30 and random.random() < 0.1):
                    client.send.rcs(
                        from_="test",
                        to=TO_NUM,
                        cards=[Card(media_url=BREAK_FREE_URL, title="Oh no! The Pokémon broke free!")]
                    )
                    finish_turn()
                    return {"status": "ok"}

                client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[Card(media_url=SHAKE_BALL_URL, title="...")]
                )

                pause()

                # Final shake
                if (health_percentage >= 90 and random.random() < 2/3) or \
                   (30 <= health_percentage < 90 and random.random() < 1/3) or \
                   (health_percentage < 30 and random.random() < 0.1):
                    client.send.rcs(
                        from_="test",
                        to=TO_NUM,
                        cards=[Card(media_url=BREAK_FREE_URL, title="Oh no! The Pokémon broke free!")]
                    )
                    finish_turn()
                    return {"status": "ok"}
                
                # If we made it here, the capture was successful
                client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    cards=[Card(media_url=ZIGZAGOON_CAPTURED_URL, title="Gotcha! Zigzagoon was caught!")]
                )
                return {"status": "ok"}
            
            case "RUN":
                print("RUN")
                return {"status": "ok"}
            
            case _:
                print(f"Unknown payload: {message.payload}")
                return {"status": "error", "message": "Unknown action"}
            



if __name__ == "__main__":
    init_battle()
    uvicorn.run(app, host="0.0.0.0", port=8000)