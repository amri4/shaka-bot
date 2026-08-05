# utils/characters.py

import json
import difflib
import re
import mycord

db = mycord.Bot()


def normalize(text: str) -> str:
    return re.sub(
        r"[^a-z0-9]",
        "",
        text.lower()
    )


def search(name: str):
    """
    Returns:
        None
        or
        {
            "name": "...",
            "claimed_by": ...,
            "claimed_at": ...
        }
    """

    name = normalize(name)

    best = None
    best_ratio = 0

    for character in db.fetchall("characters"):

        character_name = character[0]
        aliases = json.loads(character[1])

        for alias in aliases:

            alias = normalize(alias)

            # Perfect match
            if alias == name:
                return {
                    "name": character_name,
                    "claimed_by": character[2],
                    "claimed_at": character[3]
                }

            ratio = difflib.SequenceMatcher(
                None,
                alias,
                name
            ).ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best = {
                    "name": character_name,
                    "claimed_by": character[2],
                    "claimed_at": character[3]
                }

    if best_ratio >= 0.82:
        return best

    return None


def user_has_character(user_id: int):
    return db.exists(
        "characters",
        "claimed_by = ?",
        (user_id,)
    )


def get_user_character(user_id: int):
    character = db.fetchone(
        "characters",
        "claimed_by = ?",
        (user_id,)
    )

    if character is None:
        return None

    return {
        "name": character[0],
        "claimed_by": character[2],
        "claimed_at": character[3]
    }


def claim(user_id: int, name: str):
    db.update(
        "characters",
        "claimed_by = ?, claimed_at = strftime('%s','now')",
        "name = ?",
        (
            user_id,
            name
        )
    )


def unclaim(name: str):
    db.update(
        "characters",
        "claimed_by = NULL, claimed_at = NULL",
        "name = ?",
        (name,)
    )


def available(name: str):
    character = search(name)

    if character is None:
        return False

    return character["claimed_by"] is None


def exists(name: str):
    return search(name) is not None


def all():
    characters = []

    for character in db.fetchall("characters"):
        characters.append({
            "name": character[0],
            "claimed_by": character[2],
            "claimed_at": character[3]
        })

    return characters
