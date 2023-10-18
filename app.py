from __future__ import division, print_function

import sys
import os
import glob
import re
import numpy as np
import tensorflow as tf
import tensorflow as tf

from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.2
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
# Keras
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import Flask, render_template, request,session,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
import os
import pandas as pd
from werkzeug.utils import secure_filename

# import count_vect

from flask import Flask, jsonify, request
import numpy as np

import pandas as pd
import numpy as np



import re

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__,template_folder='templates')
app.secret_key = 'super-secret-key'

# Model saved with Keras model.save()
MODEL_PATH ='final_model.h5'

# Load your trained model
model = load_model(MODEL_PATH)




def model_predict(img_path, model):
    print(img_path)
    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   
# x = preprocess_input(x)

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds=""
        
    elif preds==1:
        preds="120 Tree's In The Image                                . Accuracy: 0.66% "
    elif preds==2:
        preds="59 Tree's In The Image                                  . Accuracy: 0.66% "
    elif preds==3:
        preds="20 Tree's In The Image                                  . Accuracy: 0.88%   "
    elif preds==4:
        preds="87 Tree's In The Image                                  . Accuracy: 0.66% "
    elif preds==5:
        preds="69 Tree's In The Image                                  .Accuracy: 0.56% " 
    elif preds==6:
        preds="34 Tree's In The Image .                                .Accuracy: 0.98%  "
    elif preds==7:
        preds="21 Tree's In The Image                                 .Accuracy: 0.98% "  
    elif preds==8:
         preds="555 Tree's In The Image                                 .Accuracy: 0.46% "
    elif preds==9:
        preds="1 Tree's In The Image                                     . Accuracy: 0.98% "
    elif preds==10:
        preds="223 Tree's In The Image                                   .Accuracy: 0.57% "
    elif preds==11:
        preds="265 Tree's In The Image                                   . Accuracy: 0.40% "
    elif preds==12:
        preds="863 Tree's In The Image                                   . Accuracy: 0.39% "
    elif preds==13:
        preds="265 Tree's In The Image                                   . Accuracy: 0.36% "
    elif preds==14:
        preds="365 Tree's In The Image                                    .Accuracy: 0.50% "
    return preds





app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = params['gmail_user']
app.config['MAIL_PASSWORD'] = params['gmail_password']
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Register(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    uname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(10), nullable=False)
    cpassword = db.Column(db.String(10), nullable=False)

class Contact(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(50),nullable=False)
    subject=db.Column(db.String(50),nullable=False)
    message=db.Column(db.String(250),nullable=False)

@app.route("/")
def Home():
    return render_template('index.html',params=params)

@app.route("/about")
def About():
    return render_template('about.html',params=params)

@app.route("/album")
def Album():
    return render_template('album.html',params=params)

@app.route("/register", methods=['GET','POST'])
def register():
    if(request.method=='POST'):
        name = request.form.get('name')
        uname = request.form.get('uname')
        email= request.form.get('email')
        password= request.form.get('password')
        cpassword= request.form.get('cpassword')

        user=Register.query.filter_by(email=email).first()
        if user:
            flash('Account already exist!Please login','success')
            return redirect(url_for('register'))
        if not(len(name)) >3:
            flash('length of name is invalid','error')
            return redirect(url_for('register')) 
        if (len(password))<8:
            flash('length of password should be greater than 7','error')
            return redirect(url_for('register'))
        else:
             flash('You have registtered succesfully','success')
            
        entry = Register(name=name,uname=uname,email=email,password=password,cpassword=cpassword)
        db.session.add(entry)
        db.session.commit()
    return render_template('register.html',params=params)

@app.route("/login",methods=['GET','POST'])
def login():
    if (request.method== "GET"):
        if('email' in session and session['email']):
            return render_template('dashboard.html',params=params)
        else:
            return render_template("dashboard.html", params=params)

    if (request.method== "POST"):
        email = request.form["email"]
        password = request.form["password"]
        
        login = Register.query.filter_by(email=email, password=password).first()
        if login is not None:
            session['email']=email
            return render_template('dashboard.html',params=params)
        else:
            flash("plz enter right password or email",'error')
            return render_template('dashboard.html',params=params)

@app.route("/contact",  methods=['GET','POST'])
def contact():
    if(request.method =='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        subject=request.form.get('subject')
        message=request.form.get('message')
        entry=Contact(name=name,email=email,subject=subject,message=message)
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',params=params)


@app.route("/logout", methods = ['GET','POST'])
def logout():
    session.pop('email')
    return redirect(url_for('Home')) 


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", params=params)

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)
        result=preds
        return result
    
    
    return None

if __name__ == '__main__':
    app.run(debug=True)