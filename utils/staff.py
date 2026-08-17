import mycord
from datetime import datetime, timezone


db = mycord.PunksDB()


# =========================================================
# DEFAULT STAFF HIERARCHY
# =========================================================

DEFAULT_RANKS = [
    ("Trainee", 1),
    ("Junior Moderator", 2),
    ("Moderator", 3),
    ("Senior Moderator", 4),
    ("Administrator", 5),
    ("Head Administrator", 6),
    ("Owner", 7),
]


# =========================================================
# TABLES
# =========================================================

db.create_table(
    "staff_ranks",
    """
    guild_id INTEGER,
    rank_name TEXT,
    level INTEGER,
    PRIMARY KEY (guild_id, rank_name),
    UNIQUE (guild_id, level)
    """
)

db.create_table(
    "staff_members",
    """
    guild_id INTEGER,
    user_id INTEGER,
    rank_name TEXT,
    joined_at TEXT,
    last_active TEXT,
    active_days INTEGER DEFAULT 0,
    activity_streak INTEGER DEFAULT 0,
    PRIMARY KEY (guild_id, user_id)
    """
)

db.create_table(
    "staff_command_permissions",
    """
    guild_id INTEGER,
    bot_name TEXT,
    command_name TEXT,
    required_rank TEXT,
    PRIMARY KEY (guild_id, bot_name, command_name)
    """
)

db.create_table(
    "staff_career",
    """
    guild_id INTEGER,
    user_id INTEGER,

    career_score INTEGER DEFAULT 0,

    cases_reviewed INTEGER DEFAULT 0,
    cases_resolved INTEGER DEFAULT 0,
    cases_dismissed INTEGER DEFAULT 0,

    reports_reviewed INTEGER DEFAULT 0,
    actions_executed INTEGER DEFAULT 0,

    correct_decisions INTEGER DEFAULT 0,
    overturned_cases INTEGER DEFAULT 0,
    appeals_lost INTEGER DEFAULT 0,

    promotions INTEGER DEFAULT 0,
    demotions INTEGER DEFAULT 0,
    warnings INTEGER DEFAULT 0,

    PRIMARY KEY (guild_id, user_id)
    """
)

db.create_table(
    "staff_career_history",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    guild_id INTEGER,
    user_id INTEGER,

    action TEXT,
    old_rank TEXT,
    new_rank TEXT,

    reason TEXT,
    moderator_id INTEGER,

    created_at TEXT
    """
)

db.create_table(
    "staff_promotion_config",
    """
    guild_id INTEGER,
    rank_name TEXT,

    minimum_score INTEGER DEFAULT 80,
    minimum_cases INTEGER DEFAULT 25,
    minimum_accuracy INTEGER DEFAULT 85,
    minimum_active_days INTEGER DEFAULT 14,

    automatic INTEGER DEFAULT 0,

    PRIMARY KEY (guild_id, rank_name)
    """
)


# =========================================================
# TIME
# =========================================================

def now():

    return datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# =========================================================
# ROW HELPERS
# =========================================================

def all_rows(table):

    return db.fetchall(
        table
    ) or []


# =========================================================
# HIERARCHY
# =========================================================

def ensure_ranks(guild_id):

    existing = all_rows(
        "staff_ranks"
    )

    for row in existing:

        if isinstance(row, dict):

            if row.get(
                "guild_id"
            ) == guild_id:

                return

        else:

            if row[0] == guild_id:

                return

    for name, level in DEFAULT_RANKS:

        db.insert(
            "staff_ranks",
            "guild_id, rank_name, level",
            (
                guild_id,
                name,
                level
            )
        )


def get_rank(
    guild_id,
    rank_name
):

    ensure_ranks(
        guild_id
    )

    for row in all_rows(
        "staff_ranks"
    ):

        if isinstance(row, dict):

            if (
                row.get("guild_id")
                == guild_id
                and row.get(
                    "rank_name",
                    ""
                ).lower()
                == rank_name.lower()
            ):

                return {
                    "name": row["rank_name"],
                    "level": int(
                        row["level"]
                    )
                }

        else:

            if (
                row[0] == guild_id
                and row[1].lower()
                == rank_name.lower()
            ):

                return {
                    "name": row[1],
                    "level": int(
                        row[2]
                    )
                }

    return None


def get_rank_by_level(
    guild_id,
    level
):

    ensure_ranks(
        guild_id
    )

    for row in all_rows(
        "staff_ranks"
    ):

        if isinstance(row, dict):

            if (
                row.get("guild_id")
                == guild_id
                and int(
                    row.get(
                        "level",
                        0
                    )
                ) == level
            ):

                return {
                    "name": row["rank_name"],
                    "level": int(
                        row["level"]
                    )
                }

        else:

            if (
                row[0] == guild_id
                and int(row[2])
                == level
            ):

                return {
                    "name": row[1],
                    "level": int(
                        row[2]
                    )
                }

    return None


def get_rank_level(
    guild_id,
    rank_name
):

    rank = get_rank(
        guild_id,
        rank_name
    )

    if not rank:
        return 0

    return rank["level"]


def list_ranks(
    guild_id
):

    ensure_ranks(
        guild_id
    )

    result = []

    for row in all_rows(
        "staff_ranks"
    ):

        if isinstance(row, dict):

            if row.get(
                "guild_id"
            ) != guild_id:

                continue

            result.append(
                (
                    row["rank_name"],
                    int(row["level"])
                )
            )

        else:

            if row[0] != guild_id:
                continue

            result.append(
                (
                    row[1],
                    int(row[2])
                )
            )

    return sorted(
        result,
        key=lambda x: x[1]
    )


# =========================================================
# STAFF MEMBER
# =========================================================

def get_member_rank(
    guild,
    member
):

    # Server owner is always Owner.

    if member.id == guild.owner_id:

        return get_rank_by_level(
            guild.id,
            7
        )

    ensure_ranks(
        guild.id
    )

    for row in all_rows(
        "staff_members"
    ):

        if isinstance(row, dict):

            if (
                row.get("guild_id")
                == guild.id
                and row.get("user_id")
                == member.id
            ):

                return get_rank(
                    guild.id,
                    row["rank_name"]
                )

        else:

            if (
                row[0] == guild.id
                and row[1] == member.id
            ):

                return get_rank(
                    guild.id,
                    row[2]
                )

    return None


def ensure_staff_member(
    guild,
    member,
    rank_name="Trainee"
):

    existing = get_member_rank(
        guild,
        member
    )

    if existing:

        ensure_career(
            guild.id,
            member.id
        )

        return existing

    rank = get_rank(
        guild.id,
        rank_name
    )

    if not rank:

        rank = get_rank_by_level(
            guild.id,
            1
        )

    current = now()

    db.insert(
        "staff_members",
        """
        guild_id,
        user_id,
        rank_name,
        joined_at,
        last_active,
        active_days,
        activity_streak
        """,
        (
            guild.id,
            member.id,
            rank["name"],
            current,
            current,
            0,
            0
        )
    )

    ensure_career(
        guild.id,
        member.id
    )

    return rank


# =========================================================
# CHANGE RANK
# =========================================================

def set_member_rank(
    guild,
    member,
    rank_name,
    moderator_id,
    reason
):

    new_rank = get_rank(
        guild.id,
        rank_name
    )

    if not new_rank:

        raise ValueError(
            "Unknown staff rank."
        )

    old_rank = get_member_rank(
        guild,
        member
    )

    if old_rank:

        db.update(
            "staff_members",
            "rank_name = ?",
            "guild_id = ? AND user_id = ?",
            (
                new_rank["name"],
                guild.id,
                member.id
            )
        )

    else:

        ensure_staff_member(
            guild,
            member,
            new_rank["name"]
        )

    if old_rank:

        if (
            new_rank["level"]
            > old_rank["level"]
        ):

            action = "promotion"

        elif (
            new_rank["level"]
            < old_rank["level"]
        ):

            action = "demotion"

        else:

            action = "rank_change"

    else:

        action = "appointment"

    db.insert(
        "staff_career_history",
        """
        guild_id,
        user_id,
        action,
        old_rank,
        new_rank,
        reason,
        moderator_id,
        created_at
        """,
        (
            guild.id,
            member.id,
            action,
            old_rank["name"]
            if old_rank
            else None,
            new_rank["name"],
            reason,
            moderator_id,
            now()
        )
    )

    ensure_career(
        guild.id,
        member.id
    )

    if action == "promotion":

        update_career_stat(
            guild.id,
            member.id,
            "promotions"
        )

    elif action == "demotion":

        update_career_stat(
            guild.id,
            member.id,
            "demotions"
        )

    return (
        old_rank,
        new_rank
    )


# =========================================================
# COMMAND PERMISSIONS
# =========================================================

def get_command_rank(
    guild_id,
    bot_name,
    command_name
):

    for row in all_rows(
        "staff_command_permissions"
    ):

        if isinstance(row, dict):

            if (
                row.get("guild_id")
                == guild_id
                and row.get(
                    "bot_name",
                    ""
                ).lower()
                == bot_name.lower()
                and row.get(
                    "command_name",
                    ""
                ).lower()
                == command_name.lower()
            ):

                return row[
                    "required_rank"
                ]

        else:

            if (
                row[0] == guild_id
                and row[1].lower()
                == bot_name.lower()
                and row[2].lower()
                == command_name.lower()
            ):

                return row[3]

    # Default

    return "Trainee"


def set_command_rank(
    guild_id,
    bot_name,
    command_name,
    rank_name
):

    if not get_rank(
        guild_id,
        rank_name
    ):

        raise ValueError(
            "Unknown staff rank."
        )

    found = False

    for row in all_rows(
        "staff_command_permissions"
    ):

        if isinstance(row, dict):

            if (
                row.get("guild_id")
                == guild_id
                and row.get("bot_name")
                == bot_name
                and row.get("command_name")
                == command_name
            ):

                found = True
                break

        else:

            if (
                row[0] == guild_id
                and row[1] == bot_name
                and row[2] == command_name
            ):

                found = True
                break

    if found:

        db.update(
            "staff_command_permissions",
            "required_rank = ?",
            """
            guild_id = ?
            AND bot_name = ?
            AND command_name = ?
            """,
            (
                rank_name,
                guild_id,
                bot_name,
                command_name
            )
        )

    else:

        db.insert(
            "staff_command_permissions",
            """
            guild_id,
            bot_name,
            command_name,
            required_rank
            """,
            (
                guild_id,
                bot_name,
                command_name,
                rank_name
            )
        )


def can_use_command(
    guild,
    member,
    bot_name,
    command_name
):

    if member.id == guild.owner_id:

        return True

    required = get_command_rank(
        guild.id,
        bot_name,
        command_name
    )

    current = get_member_rank(
        guild,
        member
    )

    if not current:

        return (
            required.lower()
            == "trainee"
        )

    return (
        current["level"]
        >= get_rank_level(
            guild.id,
            required
        )
    )


# =========================================================
# CAREER
# =========================================================

def ensure_career(
    guild_id,
    user_id
):

    for row in all_rows(
        "staff_career"
    ):

        if isinstance(row, dict):

            if (
                row.get("guild_id")
                == guild_id
                and row.get("user_id")
                == user_id
            ):

                return

        else:

            if (
                row[0] == guild_id
                and row[1] == user_id
            ):

                return

    db.insert(
        "staff_career",
        "guild_id, user_id",
        (
            guild_id,
            user_id
        )
    )


def get_career(
    guild_id,
    user_id
):

    ensure_career(
        guild_id,
        user_id
    )

    for row in all_rows(
        "staff_career"
    ):

        if isinstance(row, dict):

            if (
                row.get("guild_id")
                == guild_id
                and row.get("user_id")
                == user_id
            ):

                return row

        else:

            if (
                row[0] == guild_id
                and row[1] == user_id
            ):

                return row

    return None


CAREER_COLUMNS = {
    "career_score",
    "cases_reviewed",
    "cases_resolved",
    "cases_dismissed",
    "reports_reviewed",
    "actions_executed",
    "correct_decisions",
    "overturned_cases",
    "appeals_lost",
    "promotions",
    "demotions",
    "warnings"
}


def update_career_stat(
    guild_id,
    user_id,
    stat,
    amount=1
):

    if stat not in CAREER_COLUMNS:

        raise ValueError(
            "Invalid career statistic."
        )

    ensure_career(
        guild_id,
        user_id
    )

    db.update(
        "staff_career",
        f"{stat} = {stat} + ?",
        "guild_id = ? AND user_id = ?",
        (
            amount,
            guild_id,
            user_id
        )
    )


def career_value(
    career,
    name
):

    if isinstance(career, dict):

        return int(
            career.get(
                name,
                0
            ) or 0
        )

    columns = [
        "guild_id",
        "user_id",
        "career_score",
        "cases_reviewed",
        "cases_resolved",
        "cases_dismissed",
        "reports_reviewed",
        "actions_executed",
        "correct_decisions",
        "overturned_cases",
        "appeals_lost",
        "promotions",
        "demotions",
        "warnings"
    ]

    return int(
        career[
            columns.index(name)
        ] or 0
    )


def calculate_career_score(
    career
):

    cases = career_value(
        career,
        "cases_reviewed"
    )

    resolved = career_value(
        career,
        "cases_resolved"
    )

    correct = career_value(
        career,
        "correct_decisions"
    )

    overturned = career_value(
        career,
        "overturned_cases"
    )

    appeals = career_value(
        career,
        "appeals_lost"
    )

    if cases:

        accuracy = (
            correct / cases
        ) * 100

    else:

        accuracy = 0

    score = 0

    score += min(
        cases,
        30
    )

    score += min(
        resolved,
        20
    )

    score += min(
        int(
            accuracy * 0.4
        ),
        40
    )

    score -= overturned * 3
    score -= appeals * 4

    return max(
        0,
        min(
            score,
            100
        )
    )


# =========================================================
# PROMOTION CONFIGURATION
# =========================================================

def get_promotion_config(
    guild_id,
    rank_name
):

    for row in all_rows(
        "staff_promotion_config"
    ):

        if isinstance(row, dict):

            if (
                row.get("guild_id")
                == guild_id
                and row.get(
                    "rank_name",
                    ""
                ).lower()
                == rank_name.lower()
            ):

                return row

        else:

            if (
                row[0] == guild_id
                and row[1].lower()
                == rank_name.lower()
            ):

                return row

    return None


def set_promotion_config(
    guild_id,
    rank_name,
    minimum_score=80,
    minimum_cases=25,
    minimum_accuracy=85,
    minimum_active_days=14,
    automatic=0
):

    existing = get_promotion_config(
        guild_id,
        rank_name
    )

    if existing:

        db.update(
            "staff_promotion_config",
            """
            minimum_score = ?,
            minimum_cases = ?,
            minimum_accuracy = ?,
            minimum_active_days = ?,
            automatic = ?
            """,
            "guild_id = ? AND rank_name = ?",
            (
                minimum_score,
                minimum_cases,
                minimum_accuracy,
                minimum_active_days,
                automatic,
                guild_id,
                rank_name
            )
        )

    else:

        db.insert(
            "staff_promotion_config",
            """
            guild_id,
            rank_name,
            minimum_score,
            minimum_cases,
            minimum_accuracy,
            minimum_active_days,
            automatic
            """,
            (
                guild_id,
                rank_name,
                minimum_score,
                minimum_cases,
                minimum_accuracy,
                minimum_active_days,
                automatic
            )
        )


def promotion_check(
    guild_id,
    user_id
):

    career = get_career(
        guild_id,
        user_id
    )

    current_rank = None
    active_days = 0

    for row in all_rows(
        "staff_members"
    ):

        if isinstance(row, dict):

            if (
                row.get("guild_id")
                == guild_id
                and row.get("user_id")
                == user_id
            ):

                current_rank = row.get(
                    "rank_name"
                )

                active_days = int(
                    row.get(
                        "active_days",
                        0
                    ) or 0
                )

                break

        else:

            if (
                row[0] == guild_id
                and row[1] == user_id
            ):

                current_rank = row[2]
                active_days = int(
                    row[5] or 0
                )

                break

    if not current_rank:

        return {
            "eligible": False,
            "reason": "Member is not staff."
        }

    current = get_rank(
        guild_id,
        current_rank
    )

    if not current:

        return {
            "eligible": False,
            "reason": "Current rank is invalid."
        }

    if current["level"] >= 6:

        return {
            "eligible": False,
            "reason": "There is no normal rank above this one."
        }

    next_rank = get_rank_by_level(
        guild_id,
        current["level"] + 1
    )

    if not next_rank:

        return {
            "eligible": False,
            "reason": "Next rank does not exist."
        }

    config = get_promotion_config(
        guild_id,
        next_rank["name"]
    )

    if not config:

        minimum_score = 80
        minimum_cases = 25
        minimum_accuracy = 85
        minimum_active_days = 14
        automatic = False

    elif isinstance(config, dict):

        minimum_score = int(
            config.get(
                "minimum_score",
                80
            )
        )

        minimum_cases = int(
            config.get(
                "minimum_cases",
                25
            )
        )

        minimum_accuracy = int(
            config.get(
                "minimum_accuracy",
                85
            )
        )

        minimum_active_days = int(
            config.get(
                "minimum_active_days",
                14
            )
        )

        automatic = bool(
            int(
                config.get(
                    "automatic",
                    0
                )
            )
        )

    else:

        minimum_score = int(
            config[2]
        )

        minimum_cases = int(
            config[3]
        )

        minimum_accuracy = int(
            config[4]
        )

        minimum_active_days = int(
            config[5]
        )

        automatic = bool(
            int(
                config[6]
            )
        )

    cases = career_value(
        career,
        "cases_reviewed"
    )

    correct = career_value(
        career,
        "correct_decisions"
    )

    score = calculate_career_score(
        career
    )

    accuracy = (
        correct / cases * 100
        if cases
        else 0
    )

    eligible = (
        score >= minimum_score
        and cases >= minimum_cases
        and accuracy >= minimum_accuracy
        and active_days >= minimum_active_days
    )

    return {
        "eligible": eligible,
        "current_rank": current["name"],
        "next_rank": next_rank["name"],
        "score": score,
        "cases": cases,
        "accuracy": round(
            accuracy,
            1
        ),
        "active_days": active_days,
        "automatic": automatic
}
