class CommandParser:
    """
    Command parser role is to check if the users command is correct and set
    robot class parameters accordingly to robot-info-messages.
    Available commands:
        Mode changing:
            - IDL
            - MOV
            - STP
        Getting info:
            - POS
            - HOM
        Changing robot parameters:
            - SET
            - SPD
    """

    available_commands = (
    'IDL', 'MOV', 'STP', 'POS', 'HOM', 'SET', 'SPD', 'RETRACE')

    def __init__(self, robot):
        self.robot = robot

    def check_users_message_correctness(self, message):
        splitted_message = message.split()

        if len(splitted_message) not in range(1, 4):
            return self.wrong_input_format_error()

        command = splitted_message[0]
        if command not in self.available_commands:
            return self.wrong_input_format_error()

        number_of_arguments = len(splitted_message) - 1

        if command == 'SET' and number_of_arguments == 2:
            return self.check_SET_command(splitted_message)
        elif command == 'SPD' and number_of_arguments == 1:
            return self.check_SPD_command(splitted_message)
        elif number_of_arguments == 0 and command not in ('SET', 'SPD'):
            return command
        else:
            return self.wrong_input_format_error()

    def check_SET_command(self, message_list):
        try:
            y = int(message_list[1])
            z = int(message_list[2])
        except ValueError:
            return self.wrong_input_format_error()
        else:
            if -600 < y < 600 < z < 1500:
                command_to_send = 'SET {:>5} {:>5}'.format(y, z)
                return command_to_send
            else:
                return self.bad_position_error()

    def check_SPD_command(self, message_list):
        try:
            speed = int(message_list[1])
        except ValueError:
            return self.wrong_input_format_error()
        else:
            if 0 < speed < 100:
                command_to_send = 'SPD {:3}'.format(speed)
                return command_to_send
            else:
                return self.wrong_speed_error()

    def wrong_input_format_error(self):
        print('Bad input format. Write "HELP" to see all'
              'available comamnds and its arguments.')
        return False

    def no_command_error(self):
        print('There is no such a command. Write "HELP" to see all'
              'available comamnds and its arguments.')
        return False

    def bad_position_error(self):
        print('Position arguments must be in ranges:',
              '-500 < y < 500',
              '500 < z < 1500', sep='\n')
        return False

    def wrong_speed_error(self):
        print('Speed to set must be in range (0,100].')
        return False
