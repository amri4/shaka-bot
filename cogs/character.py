import mycord

db = mycord.DB()

db.create_table(
    "claims",
    """
    user_id INTEGER PRIMARY KEY,
    character TEXT UNIQUE
    """
)

print("Claims table ready!")
