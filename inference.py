import torch
import cv2
import argparse
import random
import time
import os

from operator import itemgetter
from models import Darknet
from utils.inference_utils import *
from sort import Sort

from Classes.Server import ComServer
from Classes.Robot import Robot
from Classes.CommandParser import CommandParser
from threading import Thread

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def detect(args, server, interval=1):
    weights, source, img_size, one_hand = args.weights, args.source, args.img_size, args.one_hand
    device = select_device(use_cpu=False, enable_benchmark=True)
    model = Darknet(args.cfg, img_size)
    model.load_state_dict(torch.load(weights, map_location=device)['model'])
    model.to(device).eval()

    half = args.half and device.type != 'cpu'  # half precision only supported on CUDA
    if half:
        model.half()

    # Get classes and colors
    classes = load_class_names(parse_data_cfg(args.data)['names'])
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in
              range(len(classes) + 1)]

    if source == "0":
        source = 0
    cap = cv2.VideoCapture(args.source)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not cap.isOpened():
        print("Error opening video stream!")
        if not os.path.exists(args.source):
            print("Specified path doesn't exist")
        return

    tracker = Sort(min_hits=1)
    counter = 1
    sending_freq_counter = 1
    last_objects = []
    while cap.isOpened():
        # start_inference = time.time()
        ret, frame = cap.read()
        if ret is True and counter % args.skip_frames == 0:
            # Get detections
            img = preprocess_image(frame, img_size, half)
            img = torch.from_numpy(img).unsqueeze(0).to(device)
            pred, _ = model(img)
            det = \
                non_max_suppression(pred.float(), args.conf_thres,
                                    args.nms_thres)[
                    0]

            if args.one_hand and det is not None and det.shape[0] > 1:
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
                            if len(k_objs) == len(tracked_objects) and obj[-1] != k_objs[i][-1]:
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

                        # start_sending = time.time()
                        if sending_freq_counter % 10 == 0:
                            server.send_data(
                                'SET {:>5} {:>5}'.format(x_c - 300, -y_c + 1150))
                            print(f"Point centres: ({x_c}, {y_c})")
                            print(f"Frame no. :{sending_freq_counter}")

                        # print(f"Time to send: {time.time() - start_sending}")
                        # robot.set_y_pos(x_c)
                        # robot.set_z_pos(y_c)
                last_objects.insert(0, tracked_objects)
                if len(last_objects) > 10:
                    last_objects.pop(-1)
            cv2.imshow(weights, frame)
            key = cv2.waitKey(1)
            # print(f"Inference time: {time.time() - start_inference}")
            if key & 0xFF == ord('q'):
                break
        counter += 1
        sending_freq_counter += 1
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
    parser.add_argument('--skip-frames', type=int, default=2,
                        help='take every k-th frame for calculation')
    parser.add_argument('--show-centres', action='store_true', default=False,
                        help='print centres of detection and draw it on frame')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    robot = Robot()
    parser = CommandParser(robot)
    server = ComServer(robot)

    server_receive_thread = Thread(target=server.receive_thread)
    server_receive_thread.start()
    x = 9
    while x != 10:
        command = input('>>> ')
        if server.connection is None:
            print('There\'s no client connected. '
                  'Keep waiting for connection...')
            continue

        command = parser.check_users_message_correctness(command)
        if command == 'RETRACE':
            # server.receiving_available = False
            # server_receive_thread.join()
            with torch.no_grad():
                detect(args, server)
        elif command:
            server.send_data(command)

        print(robot.p_home)
