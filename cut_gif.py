import cv2
import os
cap = cv2.VideoCapture("C:\\Users\\marci\\Videos\\LAB\\good_one.mp4")

if not cap.isOpened():
    print("Error opening video stream!")
counter = 1
while cap.isOpened():
    # start_inference = time.time()
    ret, frame = cap.read()
    if ret is True:
        cv2.imshow("1", frame)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        # elif key & 0xFF == ord('s'):
        if counter % 20 == 0:
            cv2.imwrite(f"C:\\Users\\marci\\Videos\\LAB\\frames\\{int(counter/20)}.jpg", frame)
    counter += 1