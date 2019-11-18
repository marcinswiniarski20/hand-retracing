class CommandParser:
    """
    Command parser role is to check if the users command is correct and set
    robot class parameters accordingly to robot-info-messages.
    Available commands:
        Mode changing:
            - IDL
            - MOV
            - STP
            - RETRACE
        Getting info:
            - POS
            - HOM
            - OVR
            - ZON
            - MOD
        Changing robot parameters:
            - SET
            - SPD
    """

    available_commands = (
        'IDL', 'MOV', 'STP', 'POS', 'HOM', 'SET', 'SPD', 'MOD', 'OVR', 'ZON',
        'RETRACE', 'INFO')

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
            if y in self.robot.zone['y'] and z in self.robot.zone['z']:
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
              'y: {}',
              'z: {}'.format(self.robot.zone['y'], self.robot.zone['z']),
              sep='\n')
        return False

    def wrong_speed_error(self):
        print('Speed to set must be in range (0,100].')
        return False

    def interpret_received_msg(self, message):
        command = message[2:5]

        if command == 'IDL':
            self.robot.mode = 'IDL'
            self.robot.servo_state = 'Off'
        elif command == 'MOV':
            self.robot.mode = 'MOV'
            self.robot.servo_state = 'On'
        elif command == 'POS':
            positions = message[5:].split()
            self.robot.actual_pos['x_pos'] = int(float(positions[0]))
            self.robot.actual_pos['y_pos'] = int(float(positions[1]))
            self.robot.actual_pos['z_pos'] = int(float(positions[2]))
        elif command == 'HOM':
            positions = message[5:].split()
            self.robot.p_home['x_pos'] = int(float(positions[0]))
            self.robot.p_home['y_pos'] = int(float(positions[1]))
            self.robot.p_home['z_pos'] = int(float(positions[2]))
        elif command == 'ZON':
            zone_ranges = [int(float(value)) for value in message[5:].split()]
            self.robot.zone['x'] = range(zone_ranges[0], zone_ranges[1])
            self.robot.zone['y'] = range(zone_ranges[2], zone_ranges[3])
            self.robot.zone['z'] = range(zone_ranges[4], zone_ranges[5])
        elif command == 'SPD':
            self.robot.ovr = int(message.split()[-1])
        elif command == 'MOD':
            self.robot.mode = message.split()[-1]
        elif command == 'OFF':
            self.robot.mode = 'OFF'
            self.robot.actual_pos['x_pos'] = self.robot.p_home['x_pos']
            self.robot.actual_pos['y_pos'] = self.robot.p_home['y_pos']
            self.robot.actual_pos['z_pos'] = self.robot.p_home['z_pos']
            self.robot.ovr = 10
            self.robot.servo_state = 'Off'
        else:
            pass
