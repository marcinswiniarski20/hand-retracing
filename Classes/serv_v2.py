import socket

from threading import Thread


class ComServer:
    """
    Server class which uses 'socket' module to set communication with client.
    Maximum amount of client is 1. It is used to send specified commands to
    Robot Client when requested and  receive confirmations or status info sent
    by client.

    FIELDS:
        - sock
        - server_info = (
            communication_adapter_ip,
            communication_port)
        - connection
        - client_ip
        - server_running
        - obtained_data
    """

    def __init__(self, robot, port=10002):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.communication_adapter_ip = self.get_hardware_ip()
        self.communication_port = port
        self.server_info = (
            self.communication_adapter_ip, self.communication_port)
        self.connection = None
        self.client_ip = None
        self.server_running = False
        self.robot = robot
        self.run_server()

    def run_server(self):
        if self.server_running:
            return None

        self.sock.bind(self.server_info)
        self.server_running = True

        print('Server Started!\n'
              'Server info:\n  IP: {}\n  PORT: {}'.format(*self.server_info))

        self.wait_for_client()

    def wait_for_client(self):
        if not self.server_running:
            return None

        if self.client_ip:
            return None

        print('\nWaiting for client connection...')

        self.sock.listen(1)
        self.connection, self.client_ip = self.sock.accept()

        print('Succesfully connected to {}'.format(self.client_ip))

        # send_loop = Thread(target=self.send_thread)
        # receive_loop = Thread(target=self.receive_thread)
        #
        # send_loop.start()
        # receive_loop.start()
        #
        # send_loop.join()
        # receive_loop.join()

    def receive_data(self):
        self.connection.settimeout(0.2)
        try:
            obtained_data = self.connection.recv(128)
        except ConnectionAbortedError:
            self.client_disconnected()
        except socket.timeout:
            pass
        else:
            return obtained_data.decode('utf-8')

    def send_data(self, command):
        command = command.encode('utf-8')
        try:
            self.connection.sendall(command)
        except ConnectionAbortedError:
            self.client_disconnected()

    def client_disconnected(self):
        self.connection = None
        self.client_ip = None
        self.wait_for_client()

    def receive_thread(self):
        while True:
            try:
                received_data = self.connection.recv(128)
            except ConnectionResetError:
                self.client_disconnected()
                break
            else:
                received_data = received_data.decode('utf-8')
                if len(received_data) > 0:
                    print(received_data)
                    if received_data[:3] == 'HOM':
                        self.robot.p_home = received_data[6:]

                else:
                    self.client_disconnected()

    def send_thread(self):
        while True:
            try:
                command = input('Give command: ').encode('utf-8')
                self.connection.sendall(command)
            except ConnectionAbortedError:
                self.client_disconnected()
                break

    def get_hardware_ip(self):
        """
        Checks the actual wifi or ethernet adapter ip address.
        :return: server ip address
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        server_ip = s.getsockname()[0]
        s.close()

        return server_ip


if __name__ == '__main__':
    server = ComServer()
    server.run_server()
    server.wait_for_client()
