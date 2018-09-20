cd /
cd /home/pi/CarDetection
export PYTHONPATH=/usr/lib/python3.5
python3 yolo_opencv.py -c ./yolov3-tiny.cfg -w ./yolov3-tiny.weights -cl ./yolov3.txt
