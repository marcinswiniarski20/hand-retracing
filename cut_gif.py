import cv2
import os
cap = cv2.VideoCapture("C:\\Users\\marci\\Videos\\tracker.gif")

if not cap.isOpened():
    print("Error opening video stream!")
counter = 1
while cap.isOpened():
    # start_inference = time.time()
    ret, frame = cap.read()
    if ret is True:
        cv2.imshow("1", frame)

        key = cv2.waitKey(0)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('s'):
            cv2.imwrite(f"gif_frames\{counter}.jpg", frame)
    counter += 1