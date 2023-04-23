import psutil
import openpyxl
import os
import telebot

class ProcessInfo:
    def __init__(self):
        self.process_list = []

    def refresh(self):
        self.process_list = []
        for process in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'create_time', 'num_threads', 'connections']):
            try:
                process_info = {}
                process_info['pid'] = process.info['pid']
                process_info['name'] = process.info['name']
                process_info['username'] = process.info['username']
                process_info['memory_percent'] = process.info['memory_percent']
                process_info['create_time'] = process.info['create_time']
                process_info['num_threads'] = process.info['num_threads']
                process_info['connections'] = process.info['connections']
                self.process_list.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def write_to_excel(self, filename):
        # Create a dictionary to store process information for each unique process name
        process_diet = {}

        for process in self.process_list:
            if process['memory_percent'] > 1:
            # Check if the process name is already in the dictionary
              if process['name'] in process_diet:
                # If it is, append the process information to the existing list of process information
                process_diet[process['name']].append(process)
              else:
                # If it's not, create a new list with the process information and add it to the dictionary
                process_diet[process['name']] = [process]

        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = 'Process Info'

        header_row = ['pid', 'name', 'username', 'memory percent', 'create time', 'number of threads', 'connections']
        sheet.append(header_row)

        # Loop through the dictionary and add the process information for each unique process name to the Excel file
        for process_name, process_list in process_diet.items():
            # Calculate the total memory percent for all processes with the same name
            total_memory_percent = sum(process['memory_percent'] for process in process_list)

            # Use the first process in the list to get the other information (since it will be the same for all processes with the same name)
            process_row = [process_list[0]['pid'], process_name, process_list[0]['username'], total_memory_percent,
                           str(process_list[0]['create_time']), process_list[0]['num_threads'],
                           str(process_list[0]['connections'])]
            sheet.append(process_row)

        wb.save(filename)


class ProcessClassification:
    def __init__(self):
        self.classification_dict = {
            'game': self.read_game_names('games.txt'),
        }

    def classify_processes(self, process_info):
        game_processes = []
        games = self.classification_dict['game']
        for process in process_info.process_list:
            if process['name'].lower() in games or process['memory_percent'] > 10:
                process['classification'] = 'game'
                game_processes.append(process)
            else:
                process['classification'] = 'other'
        return game_processes

    def add_game_process(self, game_name):
        if game_name not in self.classification_dict['game']:
            self.classification_dict['game'].append(game_name)
            self.write_game_names('games.txt')

    def remove_game_process(self, game_name):
        if game_name in self.classification_dict['game']:
            self.classification_dict['game'].remove(game_name)
            self.write_game_names('games.txt')

    def read_game_names(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        else:
            return ['game.exe', 'steam.exe', 'origin.exe']

    def write_game_names(self, filename):
        with open(filename, 'w') as f:
            for game_name in self.classification_dict['game']:
                f.write(game_name + '\n')


class Shutdown:
    def __init__(self):
        pass

    def shutdown(self):
        os.system('shutdown /s /t 1')


from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

process_info = ProcessInfo()
process_classification = ProcessClassification()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Telecom Bot. You can use the following commands:\n/tasklist - Get a list of running processes\n/filtergames - Get a list of running game processes\n/addgame - Add a process to the game filter\n/removegame - Remove a process from the game filter\n/shutdown - Shutdown")

@bot.message_handler(commands=['tasklist'])
def send_tasklist(message):
    process_info.refresh()
    process_info.write_to_excel('tasklist.xlsx')

    with open('tasklist.xlsx', 'rb') as f:
        bot.send_document(message.chat.id, f)

@bot.message_handler(commands=['filtergames'])
def send_filtered_tasklist(message):
    process_info.refresh()
    game_processes = process_classification.classify_processes(process_info)
    if len(game_processes) > 0:
        message_text = "Running game processes:\n"
        for process in game_processes:
            message_text += f"- {process['name']} ({process['pid']})\n"
        bot.reply_to(message, message_text)
    else:
        bot.reply_to(message, "No game processes currently running.")

@bot.message_handler(commands=['addgame'])
def send_addgame(message):
    try:
        text = message.text
        process_name = text.split()[1]
        process_classification.add_game_process(process_name)
        bot.reply_to(message, f"Process {process_name} added to game filter.")
    except Exception as e:
        bot.reply_to(message, "Failed to add game process.")

@bot.message_handler(commands=['removegame'])
def send_removegame(message):
    try:
        text = message.text
        process_name = text.split()[1]
        process_classification.remove_game_process(process_name)
        bot.reply_to(message, f"Process {process_name} removed from game filter.")
    except Exception as e:
        bot.reply_to(message, "Failed to remove game process.")

@bot.message_handler(commands=['shutdown'])
def send_shutdown(message):
    shutdown = Shutdown()
    shutdown.shutdown()
    bot.reply_to(message, "Shutting down computer...")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.infinity_polling()
