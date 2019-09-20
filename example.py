#!/usr/bin/python
from __future__ import print_function

import operator
import os
import re
import sys
import thread
import time

import cv2

from flask import Flask, jsonify, send_from_directory

sys.path.append(os.path.join(os.getcwd(),'python/'))
import darknet

CAMERA_INDEX = int(os.environ.get("CAMERA_INDEX", 1))
FRAME_INTERVAL = float(os.environ.get("FRAME_INTERVAL", 0.1))
FRAMES_DIR = os.path.join("/tmp", "frames")

PHOTO_NAME_RE = re.compile(r"motion-(.*)\.jpg")
MAX_LATEST = 40

server = Flask(__name__, static_url_path="")


@server.route('/frames/<path:path>')
def GET_frame(path):
    return send_from_directory(FRAMES_DIR, path)


@server.route('/')
def GET_root():
    return send_from_directory('static', 'index.html')


#@server.route('/<path:path>')
#def GET_static(path):
#    return send_from_directory('static', path)


class DarknetContext(object):
    def init(self):
        darknet.set_gpu(0)
        self.net = darknet.load_net("cfg/yolov3-tiny.cfg", "yolov3-tiny.weights", 0)
        self.meta = darknet.load_meta("cfg/coco.data")

    def process_image(self, path):
        detections = darknet.detect(self.net, self.meta, path)

        frame = cv2.imread(path)
        for label, confidence, location in detections:
            x, y, w, h = location

            left = int(x - w/2)
            right = int(x + w/2)
            top = int(y - h/2)
            bottom = int(y + h/2)

            # Draw a bounding box.
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Add a text label.
            cv2.rectangle(frame, (left, bottom), (right, bottom + 35), (0, 0, 255), cv2.cv.CV_FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, label, (left + 6, bottom + 29), font, 1.0, (255, 255, 255), 1)

        path = os.path.join(FRAMES_DIR, "labelled-temp.jpg")
        cv2.imwrite(path, frame)

        # Write to temp file then move because the image appears broken if we
        # download it while imwrite is in the process of writing it. For some
        # reason this does not happen with the PIL Image save function.
        final = os.path.join(FRAMES_DIR, "labelled.jpg")
        os.rename(path, final)


if(__name__ == "__main__"):
    # Make sure the photo directory exists.
    if not os.path.isdir(FRAMES_DIR):
        os.makedirs(FRAMES_DIR)

    # Run the web server in a separate thread.
    thread.start_new_thread(server.run, (), {'host': '0.0.0.0'})

    context = DarknetContext()
    context.init()

    capture = cv2.VideoCapture(CAMERA_INDEX)
    while capture.isOpened():
        ret, frame = capture.read()

        path = os.path.join(FRAMES_DIR, "latest.jpg")
        cv2.imwrite(path, frame)

        context.process_image(path)

        time.sleep(FRAME_INTERVAL)

