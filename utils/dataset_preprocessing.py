import sys, os
import cv2
import glob
import numpy as np


def move_imgs_with_txts(img_paths, dir_path, type_of_data):
    for img_path in img_paths:
        img_name = img_path.replace(dir_path+"\\", "")
        txt_name = img_name.replace("jpg", "txt")
        txt_path = dir_path+"/"+type_of_data+"/"+txt_name
        os.replace(img_path, dir_path+"/"+type_of_data+"/"+img_name)
        os.replace(dir_path+"/"+txt_name, txt_path)


def split_dataset(dir_path, split_ratio=0.8):
    if not os.path.exists(dir_path):
        print("Specified dir path does not exist!")
        return
    train_path = dir_path + "/train"
    test_path = dir_path + "/test"
    if not os.path.exists(train_path):
        os.makedirs(train_path)
    if not os.path.exists(test_path):
        os.makedirs(test_path)

    images = glob.glob(dir_path+"/*.jpg")
    txts = glob.glob(dir_path+"/*.txt")
    if len(images) != len(txts):
        print("Not every image has its label!")
        return
    np.random.shuffle(images)
    num_of_train_imgs = int(split_ratio*len(images))
    train_imgs = images[:num_of_train_imgs]
    test_imgs = images[num_of_train_imgs:]
    move_imgs_with_txts(train_imgs, dir_path, "train")
    move_imgs_with_txts(test_imgs, dir_path, "test")


def crop_image(image, crop_params):
    """
    Returns cropped image in way of crop_params
    :param image: image to be cropped
    :param crop_params: list of params to crop in [x, y, w, h] format
    :return: cropped image
    """
    x, y, w, h = crop_params
    return image[y:y+h, x:x+w]


def crop_images_in_dir(dir):
    images = glob.glob(dir+"/*.jpg")
    counter = 1
    for image_path in images[1:]:
        image = cv2.imread(image_path)
        image = image[60:419, :]
        # cv2.imshow('Cropped', image)
        print(f"{dir}/cropped/{counter}.jpg")
        cv2.imwrite(f"{dir}/cropped/{counter}.jpg", image)
        counter += 1

def cut_into_frames(video_path, path_to_write, period=20, wait_for_key=True, crop=True, crop_params=[731, 104, 1021, 770]):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video stream!")
        if not os.path.exists(video_path):
            print("Specified path doesn't exist")
        return

    counter = 0
    frame_number = 0
    while cap.isOpened():
        frame_number += 1
        ret, frame = cap.read()
        if ret is True:
            if crop:
                frame = crop_image(frame, crop_params)
            if frame_number % period == 0:
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(0)
                if key & 0xFF == ord('q'):
                    break
                elif key & 0xFF == ord('s'):
                    counter += 1
                    print(f"{counter}.jpg written to ../{path_to_write}")
                    cv2.imwrite(f"../{path_to_write}/{counter}.jpg", frame)
        else:
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # cut_into_frames(0, path_to_write="custom_data", crop=False)
    split_dataset("../custom_data")
    # crop_images_in_dir("../custom_data")

