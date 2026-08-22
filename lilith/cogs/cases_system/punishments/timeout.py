import discord
from datetime import timedelta

NAME = "timeout"
EMOJI = "🔇"
REQUIRE_INPUT = True
FIELD = "timeout duration"
PLACEHOLDER = "Example: 2s, 6m, 1h, 3d"

def prase_duration(value):
    value = value.strip().lower()
    if len(value) < 2:
        return None
    number = value[:-1]
    unit = value[-1]
    try:
        number = int(number)
    except ValueError:
        return None
    if number <= 0:
        return None
    units = {
        "s": timedelta(seconds=number),
        "m": timedelta(minutes=number),
        "h": timedelta(hours=number),
        "d": timedelta(days=number)
    }
    return units.get(unit)

async def apply(guild, member, duration):
    duration = parse_duration(duration)
    if duration is None:
        return False
    await member.timeout(duration=duration)
    return True
