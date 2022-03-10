from email.errors import InvalidMultipartContentTransferEncodingDefect
import os
import pathlib
# from tracemalloc import start
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
########## Add YOLOv2 libs ###############
import time
import urllib
import numpy as np
import pandas as pd
import imageio
import io
import matplotlib.pyplot as plt
import cv2
from PIL import Image
# import tensorflow as tf
# from darkflow.net.build import TFNet
import json
from flask import Flask, request, jsonify, Response
import torch
import tensorflow as tf

def prediction(image):
    #best.pt is the weights file thats needs to be changed
    model = torch.hub.load('ultralytics/yolov5', 'custom', 'nano300.pt') 
    image = imageio.imread(image, pilmode='RGB')
    results = model(image)
    return results.pandas().xyxy[0]


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        print("POST request was made")
        file = request.files.get('file')
        
        if file is None or file.filename == "":
            return jsonify({"error": "nothing in file"})

        try:

            image_bytes = file.read()
            start_time = time.time()
            result = prediction(image_bytes)
            end_time = time.time()

            for k in result.iterrows():
                print(k[1])
            list_result = [{str(k[1]['name']):k[1]['confidence']} for k in result.iterrows()]
            list_result.append({"Response_time":end_time - start_time})

            output = str(list_result).replace("'",'"')
            print(output)
            return jsonify({'result': output})
        except Exception as e:
            return jsonify({"error???": str(e)})

    return "App is running, welcome! Health: OK"


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080)