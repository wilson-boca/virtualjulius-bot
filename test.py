import telegram
from telebot import bot_token, URL

bot = telegram.Bot(token='1276054342:AAFnzpUenolykLvOns7CS1ItnuFsNOFiRvU')
print(bot.get_me())
bot.setWebhook()
s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=bot_token))
print(s)
