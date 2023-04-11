import time
import psutil
import random

class Sender:
    def sendMessage(self, message):
        print(message)

class ActivityRecognizer:
    def __init__(self):
        self.refresh()

    def refresh(self):
        self.pids = psutil.pids()

    def getActivityType(self):
        self.refresh()
        index = random.randint(0, len(self.pids)-1)
        pid = self.pids[index]
        process = psutil.Process(pid)
        return process.name()

class PowerController:
    def __init__(self):
        self.flag = "off"

    def getState(self):
        return self.flag

    def turnOn(self):
        self.flag = "on"

    def turnOff(self):
        self.flag = "off"

class Application:
    def __init__(self):
        self.sender = Sender()
        self.activityRecognizer = ActivityRecognizer()
        self.powerController = PowerController()
        self.powerController.turnOn()

    def run(self):
        while True:
            time.sleep(0.5)
            message = "PC is " + self.powerController.getState() + ", application '" + self.activityRecognizer.getActivityType() + "' is running."
            self.sender.sendMessage(message)

if __name__ == '__main__':
    app = Application()
    app.run()
