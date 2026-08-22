import importlib
import pkgutil
from discord.ext import commands


async def load(bot, package):

    package = importlib.import_module(package)

    for info in pkgutil.iter_modules(package.__path__):

        if info.name == "cog":
            continue

        module = importlib.import_module(
            f"{package.__name__}.{info.name}"
        )

        for obj in vars(module).values():

            if isinstance(obj, commands.Command):
                bot.add_command(obj)

            if getattr(obj, "__cog_listener__", False):

                for name in obj.__cog_listener_names__:
                    bot.add_listener(obj, name)
