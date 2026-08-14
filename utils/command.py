from discord.ext import commands


def command(category, description=None, **kwargs):
    def decorator(func):

        cmd = commands.command(
            description=description,
            **kwargs
        )(func)

        cmd.extras["help_category"] = category

        return cmd

    return decorator
