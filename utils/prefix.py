def get_prefix(bot, message):
    name = bot.user.name

    if message.content.lower().startswith(name.lower()):
        return message.content[:len(name)]

    return name
