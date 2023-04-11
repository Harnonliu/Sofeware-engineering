import os
import telebot
import psutil

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['fetch_processes'])
def fetch_processes(message):
    process_info_manager.refresh_process_info()
    with open('processes.txt', 'w') as f:
        for process in process_info_manager.processes:
            f.write(f"PID: {process['pid']}, Name: {process['name']}\n")
    bot.send_document(message.chat.id, open('processes.txt', 'rb'))
    os.remove('processes.txt')

@bot.message_handler(commands=['fetch_game_processes'])
def fetch_game_processes(message):
    game_processes = process_classifier.classify_processes()
    with open('game_processes.txt', 'w') as f:
        for process in game_processes:
            f.write(f"PID: {process['pid']}, Name: {process['name']}\n")
    bot.send_document(message.chat.id, open('game_processes.txt', 'rb'))
    os.remove('game_processes.txt')

@bot.message_handler(commands=['terminate_process'])
def terminate_process(message):
    process_name = message.text.split()[1]
    found = False
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            process.terminate()
            bot.reply_to(message, f"Terminated process: {process_name}")
            found = True
            break
    if not found:
        bot.reply_to(message, f"Process {process_name} not found")

@bot.message_handler(commands=['echo_all'])
def echo_all(message):
    bot.reply_to(message, message.text)

@bot.message_handler(func=lambda message: True)
def default_message_handler(message):
    bot.reply_to(message, "Unknown command. Please use a valid command.")

# Start bot
bot.infinity_polling()
