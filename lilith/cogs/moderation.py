import discord
from discord.ext import commands
import mycord
from utils.command import command

db = mycord.PunksDB()

db.create_table(
    "cases",
    """
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    reporter_id INTEGER NOT NULL,
    suspect_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
    """
)
CASE_STATUSES = {
    "OPEN",
    "REVIEWING",
    "RESOLVED",
    "DISMISSED"
}
