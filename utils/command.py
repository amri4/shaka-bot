from discord.ext import commands


def command(category, description=None, usage=None, **kwargs):
    def decorator(func):

        cmd = commands.command(
            description=description,
            **kwargs
        )(func)

        # Help menu category
        cmd.extras["help_category"] = category

        # Optional custom usage
        if usage is not None:
            cmd.extras["help_usage"] = usage

        return cmd

    return decorator
