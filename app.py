from Classes.serv_v2 import ComServer
from Classes.Robot import Robot
from Classes.CommandParser import CommandParser
from threading import Thread

from time import sleep
from inference import parse_args, detect

args = parse_args()
robot = Robot()
parser = CommandParser(robot)
server = ComServer(robot)

server_receive_thread = Thread(target=server.receive_thread)
server_receive_thread.start()
x = 9
while x != 10:
    sleep(0.2)
    command = input('>>> ')
    if server.connection is None:
        print('There\'s no client connected. '
              'Keep waiting for connection...')
        continue

    command = parser.check_users_message_correctness(command)
    if command == 'RETRACE':
        detect(args, server)
    elif command:
        server.send_data(command)

    print(robot.p_home)
