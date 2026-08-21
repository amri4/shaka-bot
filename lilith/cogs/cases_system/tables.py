import discord
import mycord

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
    report_reason TEXT,
    violation TEXT,
    moderator_reason TEXT,
    reviewer_id INTEGER
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
db.create_table(
    "case_actions",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    selected_by INTEGER NOT NULL,
    confirmed INTEGER NOT NULL DEFAULT 0,
    executed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    executed_at TEXT
    """
)

