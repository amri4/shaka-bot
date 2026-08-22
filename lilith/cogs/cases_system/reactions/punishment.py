import importlib
import pkgutil

from discord.ext import commands

import lilith.cogs.moderation.punishments as punishments


def get_punishments():

    result = {}

    for info in pkgutil.iter_modules(
        punishments.__path__
    ):

        module = importlib.import_module(
            f"lilith.cogs.moderation.punishments.{info.name}"
        )

        if hasattr(module, "EMOJI"):
            result[module.EMOJI] = module

    return result


selected_punishments = {}


@commands.Cog.listener()
async def on_raw_reaction_add(
    self,
    payload
):

    if payload.user_id == self.bot.user.id:
        return

    punishment = get_punishments().get(
        str(payload.emoji)
    )

    if not punishment:
        return

    key = (
        payload.message_id,
        payload.user_id
    )

    selected_punishments.setdefault(
        key,
        []
    )

    if punishment not in selected_punishments[key]:

        selected_punishments[key].append(
            punishment
        )

        print(
            f"Punishment selected: "
            f"{punishment.NAME}"
        )


async def get_selected_punishments(
    message,
    user_id
):

    return selected_punishments.get(
        (message.id, user_id),
        []
    )
