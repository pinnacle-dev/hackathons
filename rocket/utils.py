from smartrent import async_login
from dotenv import load_dotenv
import os

load_dotenv()


async def control_lock(locked: bool):
    api = await async_login(
        os.environ["SMARTRENT_EMAIL"], os.environ["SMARTRENT_PASSWORD"]
    )

    lock = api.get_locks()[0]
    await lock.async_set_locked(locked)
