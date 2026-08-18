import mycord


db = mycord.PunksDB()


# =========================================
# REMOVE OLD LILITH MODERATION SYSTEM
# =========================================

old_tables = [
    "mod_cases",
    "case_actions",
    "case_history"
]


for table in old_tables:

    db.drop_table(table)

    print(
        f"🗑️ Deleted: {table}"
    )


print(
    "✅ Old Lilith moderation system completely removed."
)
