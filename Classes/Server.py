import socket

from threading import Timer


class ServerRobot:
    """
    Server Class able to connect with only 1 client.
    """

    # region FIELDS
    sock = None
    communication_adapter_ip = None
    communication_port = None
    server_info = None
    connection = None
    client_ip = None
    check_connection_timer = None
    checking_permitted = False

    # Flags
    server_running = False
    client_connected = False

    # endregion

    def __init__(self, port=10002):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.communication_adapter_ip = self.get_hardware_ip()
        self.communication_port = port
        self.server_info = (
            self.communication_adapter_ip, self.communication_port)
        # self.run_server()

    def run_server(self):
        self.sock.bind(self.server_info)
        print('Server Started!\n'
              'Server info:\n  IP: {}\n  PORT: {}'.format(*self.server_info))
        self.server_running = True

        # self.check_connection_timer = \
        #     Timer(0.5, function=self.check_connection).start()

        # self.wait_for_robot_client()

    def check_connection(self):
        if self.checking_permitted:
            self.send_message(verbose=False, timeout=0.0001)
        else:
            pass

        self.check_connection_timer = \
            Timer(5, function=self.check_connection).start()

    def wait_for_robot_client(self):
        self.sock.listen(1)
        print('\nWaiting for client connection...')
        self.connection, self.client_ip = self.sock.accept()
        print('Succesfully connected to with {}'.format(self.client_ip))
        self.client_connected = True
        self.checking_permitted = True

    def send_message(self, message='123', timeout=0.1, verbose=True):
        if self.connection is not None:
            message = message.encode('utf-8')
            try:
                self.connection.sendall(message)
            except:
                print('An error occured while sending data!')
                return None
            else:
                return self.receive_confirmation(verbose, timeout)

    def receive_confirmation(self, verbose=True, timeout=0.1):
        self.checking_permitted = False
        self.connection.settimeout(timeout)
        try:
            confirmation = self.connection.recv(128)
        except ConnectionAbortedError:
            print('Connection has been aborted!')
            self.client_disconnected()

            return None
        except socket.timeout:
            return None
        else:
            self.connection.settimeout(None)
            confirmation = confirmation.decode('utf-8')
            if verbose:
                print('Received confirmation: ', confirmation)

            return confirmation
        finally:
            self.checking_permitted = True

    def client_disconnected(self):
        self.connection = None
        self.client_ip = None
        self.client_connected = False
        self.checking_permitted = False
        print('There\'s no client connected.')
        self.wait_for_robot_client()

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
    Serv = ServerRobot()
    while True:
        Serv.send_message(input('Give message: '))
