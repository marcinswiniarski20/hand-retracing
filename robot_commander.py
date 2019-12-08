import torch
import cv2
import argparse
import random
import time
import os

from operator import itemgetter
from models import Darknet
from inference_utils import *
from sort import Sort

from Classes.Server import ComServer
from Classes.Robot import Robot
from Classes.CommandParser import CommandParser
from threading import Thread, Timer

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, default='cfg/yolov3_hand-spp.cfg',
                        help='cfg file path')
    parser.add_argument('--data', type=str, default='data/ego.data',
                        help='.data file path')
    parser.add_argument('--weights', type=str,
                        default='weights/full_dataset.pt',
                        help='path to weights file')
    parser.add_argument('--source', type=str, default='0',
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
    parser.add_argument('--skip-frames', type=int, default=10,
                        help='take every k-th frame for calculation')
    parser.add_argument('--show-centres', action='store_true', default=False,
                        help='print centres of detection and draw it on frame')
    return parser.parse_args()


def detect(arg, src='0'):
    weights, source, img_size, one_hand = arg.weights, src, arg.img_size, arg.one_hand
    device = select_device(use_cpu=False, enable_benchmark=True)
    model = Darknet(arg.cfg, img_size)
    model.load_state_dict(torch.load(weights, map_location=device)['model'])
    model.to(device).eval()

    half = arg.half and device.type != 'cpu'  # half precision only supported on CUDA
    if half:
        model.half()

    # Get classes and colors
    classes = load_class_names(parse_data_cfg(arg.data)['names'])
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in
              range(len(classes) + 1)]

    if source == "0":
        source = 0
        cap = cv2.VideoCapture(source)
    elif source == "1":
        cap = cv2.VideoCapture('ip')
    else:
        cap = cv2.VideoCapture('./data/' + source)
    cap.set(cv2.CAP_PROP_FPS, 10)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not cap.isOpened():
        print("Error opening video stream!")
        if not os.path.exists(arg.source):
            print("Specified path doesn't exist")
        return

    if cap.isOpened():
        ret, frame = cap.read()
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        y_prescaler, z_prescaler = find_prescaler(robot, frame_width,
                                                  frame_height)

        print(y_prescaler, z_prescaler)

    tracker = Sort(min_hits=1)
    last_objects = []
    Timer(interval=1, function=send_point).start()
    while cap.isOpened():
        # start_inference = time.time()
        ret, frame = cap.read()
        if ret is True:
            # Get detections
            img = preprocess_image(frame, img_size, half)
            img = torch.from_numpy(img).unsqueeze(0).to(device)
            pred, _ = model(img)
            det = \
                non_max_suppression(pred.float(), arg.conf_thres,
                                    arg.nms_thres)[0]

            if arg.one_hand and det is not None and det.shape[0] > 1:
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

                        robot.actual_pos['y_pos'] = int(y_prescaler * x_c)
                        robot.actual_pos['z_pos'] = \
                            int(z_prescaler * y_c + robot.p_home['z_pos'])

                last_objects.insert(0, tracked_objects)
                if len(last_objects) > 10:
                    last_objects.pop(-1)
            cv2.imshow(weights, frame)
            key = cv2.waitKey(10)
            # print(f"Inference time: {time.time() - start_inference}")
            if key & 0xFF == ord('q'):
                print('Finished retracing! Waiting for another command.')
                retracing = False
                break
    cv2.destroyAllWindows()


def send_point(send_interval=0.5):
    if server.sending_available:
        if abs(robot.actual_pos['y_pos'] - robot.last_pos['y_pos']) > accuracy \
                or abs(
            robot.actual_pos['z_pos'] - robot.last_pos['z_pos']) > accuracy:
            server.send_data('0 {:>5} {:>5}'.format(robot.actual_pos['y_pos'],
                                                      robot.actual_pos[
                                                          'z_pos']))
            robot.last_pos['y_pos'] = robot.actual_pos['y_pos']
            robot.last_pos['z_pos'] = robot.actual_pos['z_pos']

    if server.client_ip and retracing:
        Timer(interval=send_interval, function=send_point).start()



def find_prescaler(robot, frame_width, frame_height):
    robot_y_range = abs(robot.zone['y'].start) + robot.zone['y'].stop
    robot_z_range = robot.zone['z'].stop - robot.zone['z'].start

    width_prescaler = robot_y_range / frame_width
    height_prescaler = robot_z_range / frame_height

    return width_prescaler, height_prescaler


robot = Robot()
command_parser = CommandParser(robot)
server = ComServer(command_parser)
args = parse_args()

accuracy = 30
retracing = False

server_receive_thread = Thread(target=server.receive_thread)
server_receive_thread.start()

while True:
    command = input()
    if server.connection is None:
        print('There\'s no client connected. '
              'Keep waiting for connection...')
        continue

    command = command_parser.check_users_message_correctness(command)

    if command == 'RETRACE':
        retracing = True
        src = command_parser.choose_available_video()
        with torch.no_grad():
                detect(args, src)
    elif command == 'INFO':
        robot.show_robot_info()
    elif type(command) == list and command[0] == 'ACC':
        accuracy = int(command[1])
    elif command:
        server.send_data(command, verbose=False)
