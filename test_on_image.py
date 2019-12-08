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
from threading import Thread

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


def detect(args, interval=1):
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
    cap = cv2.VideoCapture("./test_data/test_%03d.jpg", cv2.CAP_IMAGES)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not cap.isOpened():
        print("Error opening video stream!")
        if not os.path.exists(args.source):
            print("Specified path doesn't exist")
        return

    counter = 1
    sending_freq_counter = 1
    while cap.isOpened():
        # start_inference = time.time()
        ret, frame = cap.read()
        if ret is True:
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

                for *xyxy, conf, _, cls in det:
                    label = f"{classes[int(cls)]} {conf:.2f}"
                    plot_one_box(xyxy, frame, label=label,
                                 color=colors[int(cls)])
            cv2.imwrite(f"./test_data/output_{counter}.jpg", frame)
            key = cv2.waitKey(1)
            # print(f"Inference time: {time.time() - start_inference}")
            if key & 0xFF == ord('q'):
                break
        counter += 1
        sending_freq_counter += 1
    cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, default='cfg/yolov3_hand-spp.cfg',
                        help='cfg file path')
    parser.add_argument('--data', type=str, default='data/ego.data',
                        help='.data file path')
    parser.add_argument('--weights', type=str,
                        default='weights/full_dataset.pt',
                        help='path to weights file')
    parser.add_argument('--source', type=str, default='data/two_hands_test.mp4',
                        help='source')
    parser.add_argument('--img-size', type=int, default=416,
                        help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.75,
                        help='object confidence threshold')
    parser.add_argument('--nms-thres', type=float, default=0.7,
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
    with torch.no_grad():
        detect(args)