print("🔥🔥🔥 TEST.PY IMPORTED 🔥🔥🔥")
from utils.discord_setup import *


@listener("on_raw_reaction_add")
async def test_reaction(payload):

    print(
        "🔥🔥 REACTION EVENT FIRED",
        payload.emoji,
        payload.user_id,
        payload.message_id
    )
