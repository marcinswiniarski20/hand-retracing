class Robot:
    # region Fields
    p_home = None
    ovr = None
    x_pos = None
    y_pos = None
    z_pos = None
    mode = "START"

    # endregion


    def show_robot_info(self):
        pass

    def set_speed(self, speed):
        self.ovr = speed

    def set_x_pos(self, position):
        self.x_pos = position

    def set_y_pos(self, position):
        self.y_pos = position

    def set_z_pos(self, position):
        self.z_pos = position

    def set_mode(self, mode):
        self.mode = mode
