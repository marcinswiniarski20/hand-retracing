import torch, cv2, argparse, random, time, os, warnings, sys

from operator import itemgetter
from models import Darknet
from utils.inference_utils import *
from sort import Sort
from threading import Thread, Timer
from functools import partial

from Classes.Server import ComServer
from Classes.Robot import Robot
from Classes.CommandParser import CommandParser

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

warnings.filterwarnings('ignore', category=DeprecationWarning)


class Controller(QMainWindow):

    def __init__(self, args):
        super().__init__()
        self.robot = Robot()
        self.command_parser = CommandParser(self.robot)
        self.server = ComServer(self.command_parser)
        self.args = args
        self.retracing = False
        self.init_window()

    def init_window(self):
        self.setWindowTitle('Mitsubishi Control Panel')
        self.setWindowIcon(QIcon('icons/mits_logo.png'))
        self.setFixedSize(300, 600)

        self.create_connection_group()
        self.create_mode_group()

        # region Button - exit
        btn_exit = QPushButton('EXIT', self)
        btn_exit.setStyleSheet('background-color: darkred;'
                               'color: white;'
                               'font-weight: Bold;'
                               'font-size: 10px')
        btn_exit.setFixedSize(self.width() - 10, 30)
        btn_exit.move(5, self.height() - 35)
        btn_exit.clicked.connect(self.close)
        # endregion

        self.show()

    # region creating group boxes
    def create_connection_group(self):
        self.text_connection_info = 'Created server with ip: {}\n' \
                                    'Port: {}\n' \
                                    'Client: {}'

        connection_group = QGroupBox('Connection', self)
        connection_group.setFixedSize(self.width() - 20, 120)
        connection_group.move(10, 10)

        self.btn_run_server = QPushButton('Run Server!')
        self.btn_run_server.clicked.connect(self.click_run_server)

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
        connection_group_layout.addWidget(self.btn_run_server,
                                          alignment=alignment)

        connection_group.setLayout(connection_group_layout)

    def create_mode_group(self):
        mode_group = QGroupBox('Mode Changer', self)
        mode_group.setFixedSize(self.width() - 20, 160)
        mode_group.move(10, 140)

        self.btn_set_mode_idl = QPushButton('IDLE')
        self.btn_set_mode_mov = QPushButton('MOV')
        self.btn_start_retracing = QPushButton('START RETRACING')
        self.btn_set_mode_idl.setEnabled(False)
        self.btn_set_mode_mov.setEnabled(False)
        self.btn_start_retracing.setEnabled(False)
        self.btn_set_mode_idl.setFixedSize(200, 25)
        self.btn_set_mode_mov.setFixedSize(200, 25)
        self.btn_start_retracing.setFixedSize(200, 25)

        self.btn_set_mode_idl.clicked.connect(
            partial(self.server.send_data, 'IDL'))
        self.btn_set_mode_mov.clicked.connect(
            partial(self.server.send_data, 'MOV'))
        self.btn_start_retracing.clicked.connect(self.detect)

        pixmap_idle_mode = QPixmap('icons/idle_mode.png')
        pixmap_idle_mode = pixmap_idle_mode.scaled(40, 40)
        label_pixmap_idle_mode = QLabel()
        label_pixmap_idle_mode.setPixmap(pixmap_idle_mode)
        label_pixmap_idle_mode.setFixedSize(pixmap_idle_mode.width(),
                                            pixmap_idle_mode.height())

        pixmap_mov_mode = QPixmap('icons/mov_mode.png')
        pixmap_mov_mode = pixmap_mov_mode.scaled(40, 40)
        label_pixmap_mov_mode = QLabel()
        label_pixmap_mov_mode.setPixmap(pixmap_mov_mode)
        label_pixmap_mov_mode.setFixedSize(pixmap_mov_mode.width(),
                                           pixmap_mov_mode.height())

        pixmap_start_retrace = QPixmap('icons/start.png')
        pixmap_start_retrace = pixmap_start_retrace.scaled(40, 40)
        label_pixmap_start_retrace = QLabel()
        label_pixmap_start_retrace.setPixmap(pixmap_start_retrace)
        label_pixmap_start_retrace.setFixedSize(pixmap_start_retrace.width(),
                                                pixmap_start_retrace.height())

        mode_group_layout = QGridLayout()
        mode_group_layout.setColumnStretch(2, 4)
        mode_group_layout.addWidget(label_pixmap_idle_mode, 0, 0)
        mode_group_layout.addWidget(self.btn_set_mode_idl, 0, 1)
        mode_group_layout.addWidget(label_pixmap_mov_mode, 1, 0)
        mode_group_layout.addWidget(self.btn_set_mode_mov, 1, 1)
        mode_group_layout.addWidget(label_pixmap_start_retrace, 2, 0)
        mode_group_layout.addWidget(self.btn_start_retracing, 2, 1)

        mode_group.setLayout(mode_group_layout)

    # endregion

    # region button clicks
    def click_run_server(self):
        def update_server_info(self):
            self.server.run_server()
            self.label_info_connection.setText(
                self.text_connection_info.format(
                    self.server.communication_adapter_ip,
                    self.server.communication_port,
                    self.server.client_ip[0]))
            self.label_info_connection.setStyleSheet(
                'background-color: darkgreen;'
                'padding: 3px;'
                'color: white')

            setting_robot_actual_parameters(self)

        def setting_robot_actual_parameters(self):
            if self.server.client_ip:
                start_info_commands = ('HOM', 'POS', 'OVR', 'ZON', "MOD")
                for command in start_info_commands:
                    time.sleep(1)
                    self.server.send_data(command, verbose=False)
                    self.server.receive_data()

            self.robot.show_robot_info()
            self.btn_set_mode_mov.setEnabled(True)
            self.btn_start_retracing.setEnabled(True)
            server_receive_thread = Thread(target=self.server.receive_thread)
            server_receive_thread.start()

        self.label_info_connection.setText(
            self.text_connection_info.format(
                self.server.communication_adapter_ip,
                self.server.communication_port,
                'Waiting for client...'))
        self.btn_run_server.setEnabled(False)
        Timer(0.5, function=partial(update_server_info, self)).start()

    # endregion

    def detect(self):
        def find_prescaler(self, frame_width, frame_height):
            robot_y_range = abs(self.robot.zone['y'].start) + \
                            self.robot.zone['y'].stop
            robot_z_range = self.robot.zone['z'].stop - \
                            self.robot.zone['z'].start

            width_prescaler = robot_y_range / frame_width
            height_prescaler = robot_z_range / frame_height

            return width_prescaler, height_prescaler

        def send_point(self, send_interval=0.5):
            if self.server.sending_available:
                self.server.send_data(
                    'SET {:>5} {:>5}'.format(self.robot.actual_pos['y_pos'],
                                             self.robot.actual_pos['z_pos']))
            else:
                print('Confirmation hasn\'t been received.')

            if self.server.client_ip and self.retracing:
                Timer(interval=send_interval,
                      function=partial(send_point, self)).start()

        self.retracing = True
        weights, source, img_size, one_hand = self.args.weights, self.args.source, self.args.img_size, self.args.one_hand
        device = select_device(use_cpu=False, enable_benchmark=True)
        model = Darknet(self.args.cfg, img_size)
        model.load_state_dict(torch.load(weights, map_location=device)['model'])
        model.to(device).eval()

        half = self.args.half and device.type != 'cpu'  # half precision only supported on CUDA
        if half:
            model.half()

        # Get classes and colors
        classes = load_class_names(parse_data_cfg(self.args.data)['names'])
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in
                  range(len(classes) + 1)]

        if source == "0":
            source = 0
        cap = cv2.VideoCapture(source)
        cap.set(cv2.CAP_PROP_FPS, 10)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not cap.isOpened():
            print("Error opening video stream!")
            if not os.path.exists(self.args.source):
                print("Specified path doesn't exist")
            return

        if cap.isOpened():
            ret, frame = cap.read()
            frame_height = frame.shape[0]
            frame_width = frame.shape[1]
            y_prescaler, z_prescaler = find_prescaler(self, frame_width,
                                                      frame_height)

            print(y_prescaler, z_prescaler)

        tracker = Sort(min_hits=1)
        last_objects = []
        print(fps)
        Timer(interval=1, function=partial(send_point, self)).start()
        while cap.isOpened():
            # start_inference = time.time()
            ret, frame = cap.read()
            if ret is True:
                # Get detections
                img = preprocess_image(frame, img_size, half)
                img = torch.from_numpy(img).unsqueeze(0).to(device)
                pred, _ = model(img)
                det = \
                    non_max_suppression(pred.float(), self.args.conf_thres,
                                        self.args.nms_thres)[0]

                if self.args.one_hand and det is not None and det.shape[0] > 1:
                    det = torch.unsqueeze(max(det, key=itemgetter(5)), 0)

                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4],
                                              frame.shape).round()
                    tracked_objects = tracker.update(det[:, :5].cpu())

                    for *xyxy, conf, _, cls in det:
                        label = f"{classes[int(cls)]} {conf:.2f}"
                        plot_one_box(xyxy, frame, label=label,
                                     color=colors[int(cls)])

                    for i, obj in enumerate(tracked_objects):
                        if len(tracked_objects) == 1 and obj[-1] != 1:
                            tracked_objects[i][-1] = 1
                        if len(last_objects) > 1:
                            for k_objs in last_objects:
                                if len(k_objs) == len(tracked_objects) and obj[
                                    -1] != k_objs[i][-1]:
                                    euc_dist = np.sqrt(
                                        np.sum((k_objs - obj) ** 2, axis=1))
                                    if obj[-1] != k_objs[np.argmin(euc_dist)][
                                        -1] and k_objs[np.argmin(euc_dist)][
                                        -1] not in tracked_objects[:, -1]:
                                        tracked_objects[i][-1] = \
                                            k_objs[np.argmin(euc_dist)][-1]

                        plot_one_box(obj, frame, label=f"id: {obj[-1]}",
                                     color=colors[int(cls) + 1])

                        if obj[-1] == 1:
                            x_c, y_c = get_centres(obj[:4])
                            frame[y_c:y_c + 5, x_c:x_c + 5] = [0, 0, 255]

                            x_c = x_c - frame_width / 2
                            y_c = -1 * (y_c - frame_height / 2)

                            self.robot.actual_pos['y_pos'] = int(
                                y_prescaler * x_c)
                            self.robot.actual_pos['z_pos'] = \
                                int(z_prescaler * y_c + self.robot.p_home[
                                    'z_pos'])

                    last_objects.insert(0, tracked_objects)
                    if len(last_objects) > 10:
                        last_objects.pop(-1)
                cv2.imshow(weights, frame)
                key = cv2.waitKey(10)
                # print(f"Inference time: {time.time() - start_inference}")
                if key & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, default='nn_data/yolov3_hand-spp.cfg',
                        help='cfg file path')
    parser.add_argument('--data', type=str, default='nn_data/yolo.data',
                        help='.data file path')
    parser.add_argument('--weights', type=str,
                        default='weights/full_dataset.pt',
                        help='path to weights file')
    parser.add_argument('--source', type=str, default='videos/two_hands_test.mp4',
                        help='source')
    parser.add_argument('--img-size', type=int, default=416,
                        help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.65,
                        help='object confidence threshold')
    parser.add_argument('--nms-thres', type=float, default=0.5,
                        help='iou threshold for non-maximum suppression')
    parser.add_argument('--half', action='store_true',
                        help='half precision FP16 inference')
    parser.add_argument('--one-hand', action='store_true', default=False,
                        help='detect only one hand with the best prediction',
                        dest='one_hand')
    parser.add_argument('--skip-frames', type=int, default=3,
                        help='take every k-th frame for calculation')
    parser.add_argument('--show-centres', action='store_true', default=False,
                        help='print centres of detection and draw it on frame')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    app = QApplication(sys.argv)
    controller = Controller(args)
    sys.exit(app.exec())
