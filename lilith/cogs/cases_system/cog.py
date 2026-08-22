import importlib
import pkgutil

from discord.ext import commands


async def setup(bot):

    attributes = {}

    package = importlib.import_module(
        f"{__package__}.commands"
    )

    for info in pkgutil.iter_modules(
        package.__path__
    ):

        module = importlib.import_module(
            f"{package.__name__}.{info.name}"
        )

        for name, obj in vars(module).items():

            if isinstance(obj, commands.Command):
                attributes[name] = obj

    Cog = type(
        "Moderation",
        (commands.Cog,),
        attributes
    )

    await bot.add_cog(
        Cog()
    )
