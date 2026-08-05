import json
import mycord

db = mycord.Bot()

db.create_table(
    "characters",
    {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT UNIQUE"
    }
)

with open("characters.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for character in data:
    db.insert(
        "characters",
        {
            "id": character["id"],
            "name": character["name"]["en"]
        }
    )
