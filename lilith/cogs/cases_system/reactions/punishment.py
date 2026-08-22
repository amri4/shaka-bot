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

    print(
        f"Punishment selected: {punishment.NAME}"
)
