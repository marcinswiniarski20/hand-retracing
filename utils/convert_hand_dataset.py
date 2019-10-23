import argparse
import glob
import scipy.io
import numpy as np
import cv2
import os, shutil, sys


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def remove_dir(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)


def convert():
    # Read all annotations in folder
    annotations = glob.glob(args.annotations+"\\*.mat")
    images = glob.glob(args.images+"\\*.jpg")

    remove_dir(args.label)
    create_dir(args.label)
    for i, annotation in enumerate(annotations):
        image = cv2.imread(images[i])
        annotation = annotations[i]
        mat = scipy.io.loadmat(annotation)
        bboxes = np.transpose(mat['boxes'])
        file_name = annotation.replace(args.annotations+"\\", "").replace(".mat", "")
        for bbox in bboxes:
            bbox = [bbox]
            try:
                points = np.array([point[0] for i, point in enumerate(bbox[0][0][0][0]) if i < 4])
            except IndexError:
                print(f"Index error catched at image no. {i}")
            except:
                print(f"Something went wrong at image no.{i}")
            # print(points.max(axis=0))
            min_y, min_x = np.array(points.min(axis=0), dtype=int)
            max_y, max_x = np.array(points.max(axis=0), dtype=int)
            start_point = (min_x, min_y)
            end_point = (max_x, max_y)

            img_height, img_width, _ = image.shape
            box_width = max_x - min_x
            box_height = max_y - min_y
            x_center = (min_x + box_width/2)/img_width
            y_center = (min_y + box_height/2)/img_height
            box_height /= img_height
            box_width /= img_width
            if x_center > 1 or y_center > 1 or box_height > 1 or box_width > 1:
                print(f"image {i} {x_center} {y_center} {box_width} {box_height}")
                sys.exit()

            # path_to_label = args.label+"\\"+file_name+".txt"
            # with open(path_to_label, "a+") as file:
            #     file.write(f"0 {x_center} {y_center} {box_width} {box_height}\n")
            #     print(f"Written to {path_to_label}:\n 0 {x_center} {y_center} {box_width} {box_height}")
            # Blue color in BGR
            color = (255, 0, 0)
            # Line thickness of 2 px
            thickness = 2
            # Using cv2.rectangle() method
            # Draw a rectangle with blue line borders of thickness of 2 px
            image = cv2.rectangle(image, start_point, end_point, color, thickness)
            cv2.imshow('Image', image)
            cv2.waitKey(25)
            # cv2.waitKey(0)


if __name__ == '__main__':
    type_of_data = "validation"
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--annotations', type=str, help="path to file with annotations in .mat format",
                        default=f"C:\\Users\\marci\\Downloads\\hand_dataset\\{type_of_data}_dataset\\{type_of_data}_data"
                                "\\annotations")
    parser.add_argument('-i', '--images', type=str, help="path to file with images",
                        default=f"C:\\Users\\marci\\Downloads\\hand_dataset\\{type_of_data}_dataset\\{type_of_data}_data\\images")
    parser.add_argument("--label", type=str, default=f"C:\\Users\\marci\\Downloads\\hand_dataset\\{type_of_data}_dataset\\{type_of_data}_data"
                                "\\annotations_yolo")

    args = parser.parse_args()
    print(args)
    convert()
