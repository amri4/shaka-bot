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
    created_at TEXT NOT NULL,
    channel_id INTEGER,
    message_id INTEGER,
    report_reason TEXT
    """
)
CASE_STATUSES = {
    "OPEN",
    "REVIEWING",
    "RESOLVED",
    "DISMISSED"
}
db.create_table(
    "case_history",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    moderator_id INTEGER NOT NULL,
    event TEXT NOT NULL,
    details TEXT,
    created_at TEXT NOT NULL
    """
)
