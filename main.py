#!/usr/bin/env python2.7
#coding:utf-8
from flask import session,redirect,url_for,escape
from flask import request
from flask import render_template
from flask import jsonify,abort
from model import db,app,userinfo,event_info
import psutil
import os
from functools import wraps
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        print session.get("logged_in")
        if session.get("logged_in") and session.get("username") != None:
            return func(*args, **kwargs)
        return redirect(url_for('login', next=request.url))
    return decorated_function

@app.route('/',methods=['GET'])
@login_required
def index():
    return render_template("index.html",username=session['username'])

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if len(userinfo.query.filter_by(username=request.form['username'],password=request.form['password']).all()) == 0:
            error=u'用户名或密码错误'
            return jsonify({"error":1,"msg":error})
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            return jsonify({"error":0,"neturl":url_for("index")}) 
    else:
        return render_template("login.html")

@app.route('/monitorlist',methods=['GET'])
def monitorlist():
    return render_template("hostlist.html",username=session['username'])

@app.route('/itemlist',methods=['GET'])
def itemlist():
    return render_template("itemlist.html",username=session['username'])

@app.route('/api/eventinfo',methods=['GET'])
def eventinfo():
    eventdic={}
    eventdic["eventdata"]=[]
    eventlist=event_info.query.order_by(event_info.create_time.desc()).limit(10).all()
    for el in eventlist:
        eventdic["eventdata"].append({"ip":el.ip,"event":el.information,"createtime":str(el.create_time)})
    return jsonify(eventdic)
    

@app.route('/localinfo',methods=['GET'])
def localinfo():
    logical_cores=float(psutil.cpu_count())*2
    now_load=float(os.getloadavg()[0])
    loadpercent=now_load/logical_cores*100
    diskpercent=psutil.disk_usage('/').percent
    mempercent=psutil.virtual_memory().percent
    return jsonify({"loadpercent":loadpercent,"diskpercent":diskpercent,"mempercent":mempercent})
    

@app.route('/logout')
def loginout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for("login"))


if __name__=='__main__':
    app.run(host='0.0.0.0',port=8090,debug=True)
