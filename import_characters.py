# import_characters.py

import json
import re

import mycord
from data.characters import CHARACTERS

db = mycord.Bot()


db.create_table(
    "characters",
    """
    name TEXT PRIMARY KEY,
    aliases TEXT NOT NULL,
    claimed_by INTEGER DEFAULT NULL,
    claimed_at INTEGER DEFAULT NULL
    """
)


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def title_name(name: str) -> str:
    """
    MONKEY.D.LUFFY
    ->
    Monkey D. Luffy
    """

    parts = name.split(".")

    result = []

    for part in parts:
        if part == "D":
            result.append("D.")
        else:
            result.append(part.title())

    return clean(" ".join(result))


def aliases(name: str):
    aliases = set()

    aliases.add(name)

    words = (
        name.replace(".", "")
            .replace("-", " ")
            .replace("'", "")
            .split()
    )

    # Luffy
    aliases.add(words[-1])

    # Monkey
    aliases.add(words[0])

    # Monkey Luffy
    aliases.add(f"{words[0]} {words[-1]}")

    # MonkeyDLuffy
    aliases.add("".join(words))

    # Monkey D Luffy
    aliases.add(" ".join(words))

    # Remove D
    if "D" in words:
        without_d = [i for i in words if i != "D"]

        aliases.add(" ".join(without_d))
        aliases.add("".join(without_d))

    # Trafalgar Law
    if len(words) >= 4:
        aliases.add(f"{words[0]} {words[-1]}")

    # Water Law
    if len(words) >= 3:
        aliases.add(f"{words[-2]} {words[-1]}")

    aliases = sorted(set(clean(i) for i in aliases))

    return json.dumps(aliases)


added = 0

for character in CHARACTERS:

    name = title_name(character)

    if db.exists(
        "characters",
        "name = ?",
        (name,)
    ):
        continue

    db.insert(
        "characters",
        "name, aliases",
        (
            name,
            aliases(name)
        )
    )

    added += 1


print(f"Imported {added} characters.")
