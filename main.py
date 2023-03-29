import time

class Switch:
    def __init__(self):
        self.state = False

    def turn_on(self):
        self.state = True

    def turn_off(self):
        self.state = False

class SwitchMonitor:
    def __init__(self, switch):
        self.switch = switch
        self.runtime_data = []

    def start_monitoring(self):
        while True:
            if self.switch.state:
                start_time = time.time()
                while self.switch.state:
                    time.sleep(1)
                end_time = time.time()
                runtime = end_time - start_time
                self.runtime_data.append(runtime)

class SwitchDataUploader:
    def __init__(self, switch_monitor):
        self.switch_monitor = switch_monitor

    def upload_data(self):
        # Convert the runtime data into a graph
        # Upload the graph to the cloud
        # Send the graph to your parents' phones
        pass
