from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from functools import partial
from Classes.serv_v2 import ComServer
from Classes.Robot import Robot
from inference import main

import threading, sys, time


class ControlPanel(QMainWindow):

    def __init__(self, width=300, height=600):
        super().__init__()
        self.server = ComServer()
        self.robot = Robot()
        self.retracing_thread = threading.Thread(target=self.retrace)
        self.detection_thread = threading.Thread(
            target=partial(main, self.robot))

        self.height = height
        self.width = width

        self.retracing = False

        self.init_window()

    def init_window(self):
        self.setWindowTitle('Mitsubishi Control Panel')
        self.setWindowIcon(QIcon('mits_logo.png'))
        self.setFixedSize(self.width, self.height)

        self.create_connection_group()
        self.create_mode_group()

        btn_exit = QPushButton('EXIT', self)
        btn_exit.setStyleSheet('background-color: darkred;'
                               'color: white;'
                               'font-weight: Bold;'
                               'font-size: 10px')
        btn_exit.setFixedSize(self.width - 10, 30)
        btn_exit.move(5, self.height - 35)
        btn_exit.clicked.connect(self.close)

        btn_restart_server = QPushButton('Restart Server', self)
        btn_restart_server.setStyleSheet('background-color: orange;'
                               'color: black;'
                               'font-weight: Bold;'
                               'font-size: 10px')
        btn_restart_server.setFixedSize(self.width - 10, 30)
        btn_restart_server.move(5, self.height - 75)
        btn_restart_server.clicked.connect(self.on_click_restart_serv)
        btn_restart_server.setEnabled(False)

        self.show()

    def create_connection_group(self):
        self.text_connection_info = 'Created server with ip: {}\n' \
                                    'Port: {}\n' \
                                    'Client: {}'

        connection_group = QGroupBox('Connection', self)
        connection_group.setFixedSize(self.width - 20, 120)
        connection_group.move(10, 10)

        self.btn_connect = QPushButton('Run Server!')
        self.btn_connect.clicked.connect(self.on_click_run_server)

        self.label_info_connection = QLabel('Click "Run Server" to start!')
        self.label_info_connection.setFixedHeight(60)
        self.label_info_connection.setStyleSheet('background-color: darkred;'
                                                 'padding: 3px;'
                                                 'color: white')

        connection_group_layout = QVBoxLayout()
        connection_group_layout.addStretch(1)
        alignment = Qt.AlignBottom
        connection_group_layout.addWidget(self.label_info_connection,
                                          alignment=alignment)
        connection_group_layout.addWidget(self.btn_connect,
                                          alignment=alignment)

        connection_group.setLayout(connection_group_layout)

    def create_mode_group(self):
        mode_group = QGroupBox('Mode Changer', self)
        mode_group.setFixedSize(self.width - 20, 140)
        mode_group.move(10, 140)

        self.btn_set_mode_idl = QPushButton('IDLE')
        self.btn_set_mode_mov = QPushButton('MOV')
        self.btn_start_retracing = QPushButton('START RETRACING')
        self.btn_set_mode_idl.setEnabled(False)
        self.btn_set_mode_mov.setEnabled(False)
        self.btn_start_retracing.setEnabled(False)
        self.btn_set_mode_idl.clicked.connect(self.on_click_set_mode_IDL)
        self.btn_set_mode_mov.clicked.connect(self.on_click_set_mode_MOV)
        self.btn_start_retracing.clicked.connect(self.on_click_start_retrace)

        self.text_actual_mode = 'ACTUAL MODE: {}'
        self.label_actual_mode = QLabel(
            self.text_actual_mode.format('no connection'))
        self.label_actual_mode.setStyleSheet('padding: 3px;'
                                             'font-weight: Bold')

        mode_group_layout = QVBoxLayout()
        mode_group_layout.addStretch(1)
        alignment = Qt.AlignTop
        mode_group_layout.addWidget(self.label_actual_mode, alignment=alignment)
        mode_group_layout.addWidget(self.btn_set_mode_idl, alignment=alignment)
        mode_group_layout.addWidget(self.btn_set_mode_mov, alignment=alignment)
        mode_group_layout.addWidget(self.btn_start_retracing,
                                    alignment=alignment)

        mode_group.setLayout(mode_group_layout)

    # region buttons click

    def on_click_run_server(self):
        self.label_info_connection.setText(
            self.text_connection_info.format(
                self.server.communication_adapter_ip,
                self.server.communication_port,
                'Waiting for client...'))
        self.btn_connect.setEnabled(False)
        threading.Timer(3, function=self.start_serv).start()

    def on_click_set_mode_MOV(self):
        self.btn_start_retracing.setEnabled(False)
        self.btn_set_mode_idl.setEnabled(False)
        self.btn_set_mode_mov.setEnabled(False)
        self.server.send_data('MOV')
        threading.Timer(3, function=self.waittill_mode_MOV).start()

    def on_click_set_mode_IDL(self):
        self.btn_start_retracing.setEnabled(False)
        self.btn_set_mode_idl.setEnabled(False)
        self.btn_set_mode_mov.setEnabled(False)
        self.server.send_data('IDL')
        self.retracing = False
        threading.Timer(3, function=self.waittill_mode_IDL).start()

    def on_click_start_retrace(self):
        self.retracing = True
        self.detection_thread.start()
        self.retracing_thread.start()


        self.detection_thread.join()
        self.retracing_thread.join()

    def on_click_restart_serv(self):
        self.label_info_connection.setStyleSheet('background-color: darkred;'
                                                 'padding: 3px;'
                                                 'color: white')
        self.label_info_connection.setText(
            self.text_connection_info.format(
                self.server.communication_adapter_ip,
                self.server.communication_port,
                'Waiting for client...'))
        # self.server.client_disconnected()

    # endregion

    def waittill_mode_IDL(self):
        self.label_actual_mode.setText(self.text_actual_mode.format('IDLE'))
        self.btn_set_mode_mov.setEnabled(True)

    def waittill_mode_MOV(self):
        self.label_actual_mode.setText(self.text_actual_mode.format('MOV'))
        self.btn_start_retracing.setEnabled(True)
        self.btn_set_mode_idl.setEnabled(True)

    def start_serv(self):
        self.server.run_server()
        self.server.wait_for_client()
        self.label_info_connection.setText(
            self.text_connection_info.format(
                self.server.communication_adapter_ip,
                self.server.communication_port,
                self.server.client_ip[0]))
        self.label_info_connection.setStyleSheet('background-color: darkgreen;'
                                                 'padding: 3px;'
                                                 'color: white')
        self.label_actual_mode.setText(self.text_actual_mode.format('IDLE'))
        threading.Timer(5, function=partial(self.btn_set_mode_mov.setEnabled,
                                            True)).start()

    def retrace(self):
        if self.retracing:
            y = 300 - self.robot.y_pos
            z = 990 + 200 - self.robot.z_pos
            print(self.server.send_data('SET {:>5} {:>5}'.format(y, z)))
            self.set_pos_timer = \
                threading.Timer(0.2, function=self.retrace).start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = ControlPanel()
    sys.exit(app.exec())
