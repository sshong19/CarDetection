from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import time
import io
import picamera
import picamera.array

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# initialize the first frame in the video stream
firstFrame = None

camera = picamera.PiCamera()
time.sleep(1)
camera.resolution = (640, 480)
camera.vflip

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480))
def takeMotionImage(width, height, camera):
	with picamera.array.PiRGBArray(camera) as stream:
		camera.exposure_mode = 'auto'
		camera.awb_mode = 'auto'
		camera.capture(stream, format='rgb')
		return stream.array

firstFrame = takeMotionImage(640, 480, camera)
gray = cv2.cvtColor(firstFrame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (21,21), 0)
firstFrame = gray

try:
	while True:
                # grab the current frame
		image = takeMotionImage(640,480, camera)

                # resize the frame, convert it to grayscale, and blur it
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21, 21), 0)

                # compute the absolute difference between the current frame and first frame
		frameDelta = cv2.absdiff(firstFrame, gray)
		thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

                # dilate the thresholded image to fill in holes, then find contours on thresholded image
		thresh = cv2.dilate(thresh, None, iterations=2)
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		counter = 0
                # loop over the contours
		for c in cnts:
			 # if the contour is too small, ignore it
			if cv2.contourArea(c) < 500:
                                continue

			# compute the bounding box for the contour, draw it on the frame,
 			# and update the text
			(x, y, w, h) = cv2.boundingRect(c)
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
			counter = counter + 1

		print("Counted " + str(counter) + " motions")
		out.write(image)

except KeyboardInterrupt:
	out.release()
