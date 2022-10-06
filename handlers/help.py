from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message):
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS if command != 'help']
    bot.reply_to(message, '\n'.join(text))
