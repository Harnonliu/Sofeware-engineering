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
##########################################################################

class ProcessInfo:
    def __init__(self, pid):
        self.process = psutil.Process(pid)

    def get_pid(self):
        return self.process.pid

    def get_name(self):
        return self.process.name()

    def get_create_time(self):
        return self.process.create_time()

    def get_run_time(self):
        return psutil.Process().cpu_times().user - self.process.cpu_times().user

    def get_cpu_percent(self):
        return self.process.cpu_percent()

    def get_memory_percent(self):
        return self.process.memory_percent()

    def get_network_usage(self):
        connections = self.process.connections()
        total_sent = 0
        total_recv = 0
        for conn in connections:
            total_sent += conn.sent
            total_recv += conn.recv
        return (total_sent, total_recv)

class ProcessClassifier:
    def __init__(self):
        self.games = ["game1", "game2", "game3"] # Replace with actual game names
        self.platforms = ["steam", "epicgames", "origin"] # Replace with actual game platform names

    def classify_processes(self):
        game_processes = []
        for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            name = process.info['name']
            cpu_percent = process.info['cpu_percent']
            memory_percent = process.info['memory_percent']
            if any(game_name in name.lower() for game_name in self.games):
                game_processes.append(process)
            elif any(platform_name in name.lower() for platform_name in self.platforms):
                game_processes.append(process)
            elif cpu_percent > 30 or memory_percent > 30:
                game_processes.append(process)
        return game_processes

    def terminate_process_by_name(self, process_name):
        found = False
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == process_name:
                process.terminate()
                found = True
                break
        return found

    def terminate_process_by_pid(self, pid):
        try:
            process = psutil.Process(pid)
            process.terminate()
            return True
        except psutil.NoSuchProcess:
            return False
