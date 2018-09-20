
#Vehicle Detection using YOLOv3#

import cv2
import argparse
import numpy as np
import time
import picamera
import picamera.array
import datetime

#Arguments required
ap = argparse.ArgumentParser()
ap.add_argument('-c', '--config', required=True,
                help = 'path to yolo config file')
ap.add_argument('-w', '--weights', required=True,
                help = 'path to yolo pre-trained weights')
ap.add_argument('-cl', '--classes', required=True,
                help = 'path to text file containing class names')
args = ap.parse_args()
#Take an image with PiCamera instance and return an array of image bytes
def takeMotionImage(width, height, camera):
        with picamera.array.PiRGBArray(camera) as stream:
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto'
                camera.capture(stream, format='rgb')
                return stream.array
# Get the output layers from the neural network
def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers

scale = 0.00392

#Reading class names(car,truck,bicycle,etc.) from the text file yolov3.txt 
classes = None
with open(args.classes, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

#Generating different colored boxes for each class
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

#Read pre-trained weights model and the configuration file
net = cv2.dnn.readNet(args.weights, args.config)

#Setup camera
camera = picamera.PiCamera()
time.sleep(1)
camera.resolution = (640, 480)
camera.vflip

try:
	while True:
                #Take the image with specified resolution
		image = takeMotionImage(640, 480, camera)
		filename = "output/"+datetime.datetime.now().strftime("%M%S.%f_") + ".jpg"
		cv2.imwrite(filename, image)
		tic = time.time()
		#Preparing the input image to run through the deep neural network
		blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=True)
		net.setInput(blob)
		outs = net.forward(get_output_layers(net))

		#initialization
		class_ids = []
		confidences = []
		conf_threshold = 0.5
		ms_threshold = 0.4

		# for each detetion from each output layer get the confidence, class id, bounding box params
		for out in outs:
    			for detection in out:
        			scores = detection[5:]
        			class_id = np.argmax(scores)
        			confidence = scores[class_id]
        			if confidence > 0.5: #ignoring weak detections
            				class_ids.append(class_id)
            				confidences.append(float(confidence))
		toc = time.time()

                #Open a file that will constant append data to
		f = open("output/cardata.txt", "a+")
		f.write("cars: " + str(class_ids.count(2)) + " trucks: " + str(class_ids.count(7)) + " bikes: "+ str(class_ids.count(1)) + " time: " + str(datetime.datetime.now()) + "\n")
		f.close()
		print("Number of cars: " + str(class_ids.count(2)))
		print("Number of trucks: " + str(class_ids.count(7)))
		print("Number of bikes: " + str(class_ids.count(1)))
		print("Time: " + str(toc - tic))
except KeyboardInterrupt:
	print("Finished")
