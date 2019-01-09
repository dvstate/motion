from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import cv2
from datetime import datetime
from datetime import timedelta
import RPi.GPIO as GPIO

motion_pixel_threshold = 10000
resolution = (640, 480)
camera = PiCamera()
camera.resolution = resolution
camera.framerate = 16

rawdata = PiRGBArray(camera, size=resolution)
avg_frame = None
frame_num = 0

relay_pin = 26
GPIO.setmode(GPIO.BCM) #Broadcom pin-numbering scheme
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, GPIO.HIGH)

last_motion_timestamp = None

# Wait for 3 seconds to allow camera to initialize
print("Initializing the camera...")
time.sleep(3)

try:
    for f in camera.capture_continuous(rawdata, format="bgr", use_video_port=True):
        timestamp = datetime.now()

        if last_motion_timestamp is not None:
            diff = timestamp - last_motion_timestamp
            if diff.seconds > 5:
                GPIO.output(relay_pin, GPIO.HIGH) #Turn off

        print("Processing frame {0}".format(frame_num))
        frame_num = frame_num+1
        frame = f.array

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #cv2.imwrite("/var/www/html/frame{0:05d}-step1-gray.jpg".format(frame_num), gray_frame)
    
        blur_frame = cv2.blur(gray_frame, (5,5))
        #cv2.imwrite("/var/www/html/frame{0:05d}-step2-blur.jpg".format(frame_num), blur_frame)

        if avg_frame is None:
            avg_frame = blur_frame.copy().astype("float")
            rawdata.truncate(0)
            continue

        cv2.accumulateWeighted(blur_frame, avg_frame, 0.5)
        #cv2.imwrite("/var/www/html/frame{0:05d}-step3-avg.jpg".format(frame_num), avg_frame)
    
        diff_frame = cv2.absdiff(blur_frame, cv2.convertScaleAbs(avg_frame))
        #cv2.imwrite("/var/www/html/frame{0:05d}-step4-diff.jpg".format(frame_num), diff_frame)
    
        ret, thresh_frame = cv2.threshold(diff_frame, 10, 255, cv2.THRESH_BINARY)
        #cv2.imwrite("/var/www/html/frame{0:05d}-step5-thresh.jpg".format(frame_num), thresh_frame)

        motion_pixels = cv2.countNonZero(thresh_frame)
        if motion_pixels > motion_pixel_threshold:
            print("Detected motion in {0} pixels".format(motion_pixels))

            GPIO.output(relay_pin, GPIO.LOW) #Turn on
            last_motion_timestamp = datetime.now()

            pretty_time = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, pretty_time, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imwrite("/var/www/html/frame{0:05d}-motion-{1}.jpg".format(frame_num, motion_pixels), frame)

        rawdata.truncate(0)

except:
    print("Shutting down")

finally:
    GPIO.cleanup()

