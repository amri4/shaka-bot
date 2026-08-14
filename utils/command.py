from discord.ext import commands


def command(category, description, **kwargs):
    def decorator(func):
        func.help_category = category

        cmd = commands.command(
            description=description,
            **kwargs
        )(func)

        cmd.help_category = category

        return cmd

    return decorator
