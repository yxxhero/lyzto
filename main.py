#!/usr/bin/env python2.7
#coding:utf-8
from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask import session,redirect,url_for,escape
from flask import request
from flask import render_template
from flask import jsonify,abort

app=Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/login',methods=['GET'])
def login():
    return render_template("login.html")

@app.route('/monitorlist',methods=['GET'])
def monitorlist():
    return render_template("hostlist.html")

@app.route('/itemlist',methods=['GET'])
def itemlist():
    return render_template("itemlist.html")

if __name__=='__main__':
    app.run(host='0.0.0.0',port=8090,debug=True)
