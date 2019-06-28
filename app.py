from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import re
import numpy as np
import pandas as pd
import scipy
from scipy.spatial import distance
import cv2
import json

# Keras
from keras.applications import VGG16
from keras.preprocessing import image as kimage
from keras.applications.vgg16 import preprocess_input
from keras.models import load_model

import tensorflow as tf
from PIL import ExifTags, Image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from flask import jsonify


# Define a flask app
app = Flask(__name__)
#modelVGG = load_model('models/VGG16Model.hdf5')
modelVGG = VGG16(include_top=True,input_shape=(224, 224, 3))
#remove the classification layer (fc8)
modelVGG.layers.pop()

modelVGG.layers.pop()
#fix the output of the model
modelVGG.outputs = [modelVGG.layers[-3].output]

model = load_model('./models/VGG16Model_retrained.hdf5')
model.outputs = [model.layers[-1].output]

model._make_predict_function()  # Necessary
print('Model loaded. Check http://127.0.0.1:5000/')

poses = []
final=[]

desc_file = "./models/pose_descriptions.csv"

result_strength = {}
with open(desc_file, 'r') as fh_in:
  for line in fh_in:
    line = line.strip().split(',')
    result_strength[line[0]] = line[1]

result_theme = {}
with open(desc_file, 'r') as fh_in:
  for line in fh_in:
    line = line.strip().split(',')
    result_theme[line[0]] = line[2]

# Defining a graph for some reason, see below
graph = tf.get_default_graph()


def video_duration(file_path):
  cap = cv2.VideoCapture(file_path)
  fps = cap.get(cv2.CAP_PROP_FPS)
  frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
  duration = frame_count/fps
  minutes = (duration/60)
  cap.release()
  return minutes

def remove_dups(lst):
    if len(lst)>1:

        if lst[0] != lst[1]:
            return [lst[0]] + remove_dups(lst[1:])

        del lst[1]
        return remove_dups(lst)
    else:
        return lst

def model_predict(file_path, model):
  cap = cv2.VideoCapture(file_path)
  fps = cap.get(cv2.CAP_PROP_FPS)
  fps_r = round(fps)
  seconds = fps_r * 2
  count = 0
  while cap.isOpened():
      ret, frame = cap.read()

      if ret:
          cv2.imwrite('./uploads/frame.jpg'.format(count), frame)
          count += seconds
          cap.set(1, count)

          for i in glob.iglob('./uploads/frame.jpg'):
            #load image for processing through the model
            i=str(i)
            im = kimage.load_img(i, target_size=(224,224))
            im = kimage.img_to_array(im)
            im = np.expand_dims(im, axis=0)

            # prepare the image for the VGG model
            im = preprocess_input(im)

            # pull out the feature matrix from (the 3rd to last layer of) the model

            with graph.as_default():
              feat_mat = modelVGG.predict(im)

            # Save feature matrix as vector
            feature_vect = feat_mat.flatten()

            #
            feature_vect = np.asmatrix(feature_vect)

            prob = model.predict(feature_vect)

          out = (prob == prob.max(axis=1)).astype(int)
          if out[:,0]==1:
          	poses.append('Boat')
          elif out[:,1]==1:
            poses.append('Bow')
          elif out[:,2]==1:
            poses.append('Camel')
          elif out[:,3]==1:
            poses.append('Down Dog')
          elif out[:,4]==1:
            poses.append('Goddess')
          elif out[:,5]==1:
            poses.append('Tiger')
          elif out[:,6]==1:
            poses.append('Tree')
          elif out[:,7]==1:
            poses.append('Triangle')
          elif out[:,8]==1:
            poses.append('Up Dog')
          else:
            poses.append('Warrior II')
      else:
          cap.release()
          break
  final=[]
  number = len(poses)-2
  for i in range(0,int(number),2):
  	  if poses[i]==poses[i+1]==poses[i+2]:
	      final.append(poses[i])

  remove_dups(final)
  return final



@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']
        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'static', secure_filename(f.filename))
        f.save(file_path)

        result = model_predict(file_path, model)
        
        #return jsonify(result)

        str1=''
        str2=''
        str3=''

        for i in result:
          str1=str1+result_strength[i]+'; '
        str1 = str1[0:-2]
        for i in result:
          str2=str2+result_theme[i]+'; '
        str2 = str2[0:-2]
        for i in result:
          str3=str3+i+', '
        str3 = str3[0:-2]
        
        minutes = video_duration(file_path)
        minutes = round(float(minutes), 2)
        
                
        d={}
        key=str3
        d[key] = str1
        d[key]=[d[key]]
        d[key].append(str2)

        #string = key + '<br>' + d[key][0] + '<br>' + d[key][1]
        #string = key + ':' + d[key][0] + ':' + d[key][1]
        #fix = '<p>' + string + '</p>'
        string = key + '\n' +'\n' + 'This practice stretched/strengthened: '+ d[key][0] + '\n' +'\n' + 'This practice focused on: '+ d[key][1] + '\n' +'\n' + 'This practice lasted: '+ str(minutes) + ' minutes'
        #fix = '\n' + string + '\n'
        return string
        
        
        


from flask import send_file
@app.route('/get_image')
def get_image():
    filename = 'uploads\\frame.jpg'
    return send_file(filename, mimetype='image/jpg')

    return None

if __name__ == '__main__':
    # app.run(port=5002, debug=True)

    # Serve the app with gevent
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
