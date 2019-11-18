class Robot:
    """
    Robot calss which shows actual state of real manipulator. The robot we are
    using is Mitsubishi RV-12SDL.
    """
    # region Fields
    p_home = {
        'x_pos': None,
        'y_pos': None,
        'z_pos': None
    }
    last_pos = {
        'x_pos': None,
        'y_pos': None,
        'z_pos': None
    }
    actual_pos = {
        'x_pos': None,
        'y_pos': None,
        'z_pos': None
    }
    zone = {
        'x': None,
        'y': None,
        'z': None
    }
    mode = None
    ovr = None
    servo_state = None

    # endregion

    def show_robot_info(self):
        info_message = 'ROBOT INFO:\n' \
                       ' Actual position:\n' \
                       '     x: {}\n' \
                       '     y: {}\n' \
                       '     z: {}\n' \
                       ' Speed: {}\n' \
                       ' Work mode: {}'.format(
            self.actual_pos['x_pos'], self.actual_pos['y_pos'],
            self.actual_pos['z_pos'], self.ovr, self.mode)

        print(info_message)
        return info_message
