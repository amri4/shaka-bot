import discord
import mycord


db = mycord.DB()


# =========================================================
# RANKS
# =========================================================

RANKS = {
    "MEMBER": 0,
    "TRAINEE": 1,
    "JUNIOR": 2,
    "MODERATOR": 3,
    "SENIOR": 4,
    "HEAD": 5,
    "ADMINISTRATOR": 6,
    "OWNER": 7
}


RANK_NAMES = {
    0: "👤 Member",
    1: "📋 Trainee",
    2: "🔰 Junior Moderator",
    3: "🔨 Moderator",
    4: "⚔️ Senior Moderator",
    5: "🛡️ Head Moderator",
    6: "💎 Administrator",
    7: "👑 Owner"
}


# =========================================================
# DATABASE
# =========================================================

db.create_table(
    "hierarchy_roles",
    """
    guild_id INTEGER NOT NULL,
    rank INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    PRIMARY KEY (guild_id, rank)
    """
)


db.create_table(
    "mod_ratings",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    moderator_id INTEGER NOT NULL,
    rated_by INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    feedback TEXT,
    created_at TEXT NOT NULL
    """
)


db.create_table(
    "hierarchy_history",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    moderator_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    old_rank INTEGER,
    new_rank INTEGER,
    details TEXT,
    created_at TEXT NOT NULL
    """
)


# =========================================================
# RANK VALUE
# =========================================================

def rank_value(rank):

    if isinstance(rank, int):
        return rank

    return RANKS.get(
        str(rank).upper(),
        RANKS["MEMBER"]
    )


# =========================================================
# RANK NAME
# =========================================================

def rank_name(rank):

    return RANK_NAMES.get(
        rank,
        RANK_NAMES[RANKS["MEMBER"]]
    )


# =========================================================
# GET ROLE ID
# =========================================================

def get_role_id(
    guild_id,
    rank
):

    rank = rank_value(rank)

    data = db.fetchone(
        "hierarchy_roles",
        "guild_id = ? AND rank = ?",
        (
            guild_id,
            rank
        )
    )

    if not data:
        return None

    return data[2]


# =========================================================
# GET ROLE
# =========================================================

def get_role(
    guild,
    rank
):

    role_id = get_role_id(
        guild.id,
        rank
    )

    if not role_id:
        return None

    return guild.get_role(
        role_id
    )


# =========================================================
# GET MEMBER RANK
# =========================================================

def get_rank(
    member
):

    guild = member.guild

    # The actual Discord server owner
    # is always Owner.

    if member.id == guild.owner_id:

        return RANKS["OWNER"]

    highest = RANKS["MEMBER"]

    for rank in range(
        RANKS["ADMINISTRATOR"],
        RANKS["TRAINEE"] - 1,
        -1
    ):

        role = get_role(
            guild,
            rank
        )

        if role and role in member.roles:

            highest = rank

            break

    return highest


# =========================================================
# HAS RANK
# =========================================================

def has_rank(
    member,
    required_rank="MEMBER"
):

    user_rank = get_rank(
        member
    )

    required_rank = rank_value(
        required_rank
    )

    return user_rank >= required_rank


# =========================================================
# CAN MANAGE MEMBER
# =========================================================

def can_manage(
    actor,
    target
):

    guild = actor.guild

    # Server owner can manage anyone.

    if actor.id == guild.owner_id:

        return True

    # Nobody can manage themselves.

    if actor.id == target.id:

        return False

    actor_rank = get_rank(
        actor
    )

    target_rank = get_rank(
        target
    )

    return actor_rank > target_rank


# =========================================================
# CAN ASSIGN RANK
# =========================================================

def can_assign_rank(
    actor,
    target_rank
):

    guild = actor.guild

    target_rank = rank_value(
        target_rank
    )

    # Owner rank can NEVER be assigned.

    if target_rank == RANKS["OWNER"]:

        return actor.id == guild.owner_id

    # Server owner can assign every rank
    # below Owner.

    if actor.id == guild.owner_id:

        return True

    actor_rank = get_rank(
        actor
    )

    # You can only assign ranks below yourself.

    return target_rank < actor_rank


# =========================================================
# ENSURE HIERARCHY ROLES
# =========================================================

async def ensure_roles(
    guild,
    bot_member
):

    for rank in range(
        RANKS["MEMBER"],
        RANKS["OWNER"] + 1
    ):

        name = RANK_NAMES[
            rank
        ]

        role = get_role(
            guild,
            rank
        )

        # Search by name if database
        # entry is missing.

        if not role:

            role = discord.utils.get(
                guild.roles,
                name=name
            )

        # Create role if missing.

        if not role:

            try:

                role = await guild.create_role(
                    name=name,
                    reason="Hierarchy system setup"
                )

            except (
                discord.Forbidden,
                discord.HTTPException
            ):

                continue

        # Save role ID.

        if db.exists(
            "hierarchy_roles",
            "guild_id = ? AND rank = ?",
            (
                guild.id,
                rank
            )
        ):

            db.update(
                "hierarchy_roles",
                "role_id = ?",
                "guild_id = ? AND rank = ?",
                (
                    role.id,
                    guild.id,
                    rank
                )
            )

        else:

            db.insert(
                "hierarchy_roles",
                """
                guild_id,
                rank,
                role_id
                """,
                (
                    guild.id,
                    rank,
                    role.id
                )
            )

    await position_roles(
        guild,
        bot_member
    )


# =========================================================
# POSITION ROLES
# =========================================================

async def position_roles(
    guild,
    bot_member
):

    bot_top_role = bot_member.top_role

    roles = []

    for rank in range(
        RANKS["MEMBER"],
        RANKS["OWNER"] + 1
    ):

        role = get_role(
            guild,
            rank
        )

        if not role:
            continue

        if role.managed:
            continue

        # Discord will not let the bot
        # move roles above its highest role.

        if role >= bot_top_role:
            continue

        roles.append(
            role
        )

    # Member at bottom,
    # Owner at top.

    for position, role in enumerate(
        roles,
        start=1
    ):

        try:

            await role.edit(
                position=position,
                reason="Hierarchy role ordering"
            )

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            pass


# =========================================================
# SET MEMBER RANK
# =========================================================

async def set_rank(
    actor,
    target,
    target_rank
):

    guild = actor.guild

    target_rank = rank_value(
        target_rank
    )

    # Cannot change yourself.

    if actor.id == target.id:

        return False, (
            "❌ You cannot change your own rank."
        )

    # Cannot manage someone equal/higher.

    if not can_manage(
        actor,
        target
    ):

        return False, (
            "❌ You can only manage members "
            "below your own rank."
        )

    # Cannot assign Owner.

    if target_rank == RANKS["OWNER"]:

        return False, (
            "❌ The Owner rank belongs only "
            "to the actual server owner."
        )

    # Cannot assign equal/higher rank.

    if not can_assign_rank(
        actor,
        target_rank
    ):

        return False, (
            "❌ You cannot assign a rank equal "
            "to or higher than your own."
        )

    target_role = get_role(
        guild,
        target_rank
    )

    if not target_role:

        return False, (
            "❌ That hierarchy role does not exist."
        )

    old_rank = get_rank(
        target
    )

    roles_to_remove = []

    for rank in range(
        RANKS["MEMBER"],
        RANKS["ADMINISTRATOR"] + 1
    ):

        role = get_role(
            guild,
            rank
        )

        if role and role in target.roles:

            roles_to_remove.append(
                role
            )

    try:

        if roles_to_remove:

            await target.remove_roles(
                *roles_to_remove,
                reason="Hierarchy rank change"
            )

        await target.add_roles(
            target_role,
            reason="Hierarchy rank change"
        )

    except discord.Forbidden:

        return False, (
            "❌ I cannot manage that role. "
            "Make sure my bot role is above "
            "the hierarchy roles."
        )

    except discord.HTTPException:

        return False, (
            "❌ Discord rejected the role change."
        )

    # Audit history.

    db.insert(
        "hierarchy_history",
        """
        guild_id,
        target_id,
        moderator_id,
        action,
        old_rank,
        new_rank,
        details,
        created_at
        """,
        (
            guild.id,
            target.id,
            actor.id,
            "RANK_CHANGED",
            old_rank,
            target_rank,
            None,
            discord.utils.utcnow().isoformat()
        )
    )

    return True, (
        f"✅ {target.mention} is now "
        f"**{rank_name(target_rank)}**."
)
