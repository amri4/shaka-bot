import mycord

db = mycord.DB()

db.drop_table("claims")
db.drop_table("claim_panel")

print("✅ Claims tables deleted!")
