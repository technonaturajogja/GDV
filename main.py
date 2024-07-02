import cv2
import numpy as np
import serial
import threading
import time

ser = serial.Serial('/dev/ttyACM0',115200,bytesize=8,parity="N",stopbits=1,timeout=None)

data = np.zeros(6, dtype=np.uint8)

time.sleep(1)

data[0] = 0x73
data[1] = 1
data[2] = 200
data[3] = 0
data[4] = 200
data[5] = 0x64

cap = cv2.VideoCapture(0)
cap.set(3, 160)
cap.set(4, 120)
in1 = 4
in2 = 17
in3 = 27
in4 = 22
en1 = 23
en2 = 24
cx = 0
cy = 0

def writing():
    global data
    while True:
        ser.write(data)
        time.sleep(0.01)

def procces_scan():
    global cx
    global cy
    while True:
        _, frame = cap.read()
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define red color range
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])

        mask = cv2.inRange(hsv_frame, lower_red1, upper_red1) + cv2.inRange(hsv_frame, lower_red2, upper_red2)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by area (optional)
        valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]


        if valid_contours:
            largest_contour = max(valid_contours, key=cv2.contourArea)
            M = cv2.moments(largest_contour)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)  # Mark the center

        cv2.imshow("Frame",frame)

        if cv2.waitKey(1) & 0xff == ord('q'):   # 1 is the time in ms
            cap.release()
            cv2.destroyAllWindows()            
def sending_data():
    global cx, data
    while True: 
        error = cx - 80
        if cx > 70 and cx < 90:
            print ("lurus")
            single_L = 140 
            single_R = 140 
        elif cx > 90 and cx < 125:
            print ("belok kanan")
            single_L = 180
            single_R = 40
        elif cx < 70 and cx < 35:
            print ("belok kiri")
            single_L = 40
            single_R = 180
        elif cx > 125 and cx < 160:
            print("patah kanan")
            single_L = 200
            single_R = 40
        elif cx > 0 and cx < 35:
            print("patah kiri")
            single_L = 40
            single_R = 200
        
        # else:
        #     single_L = 0
        #     single_R = 0
        # single_R = 160 - error * 0.5
        # single_L = 160 + error * 0.5

        data[1] = 1  # Motor direction: 1 for forward
        data[2] = single_L
        data[3] = 0  # Motor direction: 0 is actually for move forward to
        data[4] = single_R

        print("-------------------------------")
        print("Speed left : ", single_L)
        print("Speed right : ", single_R)
        print("CX : ", cx)
        print("-------------------------------")

t1 = threading.Thread(target=writing)
t2 = threading.Thread(target=procces_scan)
t3 = threading.Thread(target=sending_data)

t1.start()
t2.start()
t3.start()

t1.join()
t2.join()
t3.join()
