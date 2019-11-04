class Robot:
    # region Fields
    p_home = None
    ovr = None
    x_pos = None
    y_pos = 0
    z_pos = 0
    mode = "START"

    # endregion

    def set_speed(self, speed):
        if speed in range(101):
            self.ovr = speed
            return True
        else:
            return False

    def set_y_pos(self, position):
        self.y_pos = position

    def set_z_pos(self, position):
        self.z_pos = position

    def set_mode(self, mode):
        self.mode = mode
