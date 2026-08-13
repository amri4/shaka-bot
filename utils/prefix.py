from config import BOT_PREFIX

def get_prefix(bot, message):
    if message.content.lower().startswith(BOT_PREFIX.lower()):
        return message.content[:len(BOT_PREFIX)]

    return []
