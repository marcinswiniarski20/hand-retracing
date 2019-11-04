import threading
from inference import main

from Classes.Robot import Robot
from Classes.Server import ServerRobot
from functools import partial


class Application:

    def __init__(self):
        self.robot = Robot()
        self.serv = ServerRobot()

        self.detection_thread = threading.Thread(
            target=partial(main, self.robot))
        self.communication_thread = threading.Thread(target=self.send_loop)

        self.detection_thread.start()

        self.communication_thread.start()

        self.detection_thread.join()
        self.communication_thread.join()

    def send_loop(self):
        while True:
            message = input('Give command: ')
            if message[:3] == 'MOV':
                received_message = self.serv.send_message(message,
                                                          verbose=False)
                print(received_message)
                self.check_connection_timer = \
                    threading.Timer(10, function=self.printka).start()
                break
            received_message = self.serv.send_message(message, verbose=False)
            print(received_message)

    def printka(self):
        y = 300 - self.robot.y_pos
        z = 990 + 200 - self.robot.z_pos

        self.serv.send_message('SET {:>5} {:>5}'.format(y, z))

        self.check_connection_timer = \
            threading.Timer(0.2, function=self.printka).start()


if __name__ == '__main__':
    app = Application()
