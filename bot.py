import telebot
bot = telebot.TeleBot('6203364575:AAF4CYl8LJVsolhyUo7pT8HyZSAyCAtf9aE')
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
 bot.reply_to(message, "Howdy, how are you doing?")
@bot.message_handler(func=lambda message: True)
def echo_all(message):
 bot.reply_to(message, message.text)
bot.infinity_polling()