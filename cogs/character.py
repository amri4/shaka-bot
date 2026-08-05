import json
import mycord

db = mycord.DB()

db.create_table(
    "characters",
    """
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
    """
)

with open("characters.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for character in data["characters"]:
    db.insert(
        "characters",
        "id, name",
        (
            character["id"],
            character["name"]["en"]
        )
    )

db.close()
