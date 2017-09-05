#!/usr/bin/env python2.7
#coding:utf-8
from flask import session,redirect,url_for,escape
from flask import request
from flask import render_template
from flask import jsonify,abort
from model import db,app,userinfo,event_info,host_info
import psutil
import os
import time
from functools import wraps
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get("logged_in") and session.get("username") != None:
            return func(*args, **kwargs)
        return redirect(url_for('login', next=request.url))
    return decorated_function

@app.route('/',methods=['GET'])
@login_required
def index():
    return render_template("index.html",username=session['username'])

@app.route('/hosttree',methods=['GET'])
@login_required
def hosttree():
    return render_template("tree.html",username=session['username'])

@app.route('/treedata',methods=['GET'])
@login_required
def treedata():
    data = [{"title": '业务机器',"type": 'folder',"products": [{"title": 'iPhone',"type": 'item',"attr":{"id":"1"}}],"attr":{"id":"2"}}] 
    return jsonify(data)


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
@login_required
def monitorlist():
    return render_template("hostlist.html",username=session['username'])

@app.route('/hostdetails',methods=['GET'])
@login_required
def hostdetails():
    id = request.args.get('id',None)
    if id:
        return render_template("tree.html",username=session['username'],id=id)
    else:
        return jsonify({"error":1,"msg":"no id"})

@app.route('/itemlist',methods=['GET'])
@login_required
def itemlist():
    return render_template("itemlist.html",username=session['username'])

@app.route('/api/eventinfo',methods=['GET'])
@login_required
def eventinfo():
    eventdic={}
    eventdic["eventdata"]=[]
    eventlist=event_info.query.order_by(event_info.create_time).limit(10).all()
    for el in eventlist:
        eventdic["eventdata"].append({"id":el.id,"ip":el.ip,"event":el.information,"createtime":str(el.create_time)})
    return jsonify(eventdic)
    
@app.route('/deletehost',methods=['GET'])
@login_required
def deletehost():
    id=request.args.get('id',None)
    if id:
        try:
            mod = host_info.query.filter_by(id=id).first()
            db.session.delete(mod)
            db.session.commit()
        except Exception,e:
            return jsonify({"error":1,"msg":str(e)})
        else:
            return jsonify({"error":0,"msg":u"删除成功"})
    else:
        return jsonify({"error":1,"msg":u"参数错误"})

@app.route('/api/hostlistinfo',methods=['GET'])
def hostlistinfo():
    hostinfodic={}
    hostinfodic["hostinfodata"]=[]
    hostinfolist=host_info.query.all()
    for hl in hostinfolist:
        if time.time() - time.mktime(time.strptime(str(hl.updatetime),"%Y-%m-%d %H:%M:%S"))>=120:
            hostinfodic["hostinfodata"].append({"id":hl.id,"ip":hl.ip,"description":hl.description,"updatetime":str(hl.updatetime),"status":1})
        else:
            hostinfodic["hostinfodata"].append({"id":hl.id,"ip":hl.ip,"description":hl.description,"updatetime":str(hl.updatetime),"status":0})
    return jsonify(hostinfodic)

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


@app.route('/api/posthostinfo',methods=['POST'])
def posthostinfo():
    if request.form.get("host_info",None):
         info_dict=request.form["host_info"]
         ip=eval(info_dict)["ip_dict"]['gatewayifaceip']
         description=eval(info_dict)["description"]
         try:
             info_result=host_info.query.filter_by(ip=ip).all()
             if len(info_result)==0:
                 db.session.add(host_info(ip=ip,description=description,information=info_dict))
                 db.session.add(event_info(ip=ip,information=u"加入监控队列",create_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                 db.session.commit()
             else:
                 update_sql=host_info.query.filter_by(ip=ip).first()
                 update_sql.information=info_dict
                 update_sql.description=description
                 db.session.commit()
         except Exception,e:
             return jsonify({"error":1,"msg":str(e)})
         else:
             return jsonify({"error":0})
    else:
        return jsonify({"error":1,"msg":"info Incomplete"})


if __name__=='__main__':
    app.run(host='0.0.0.0',port=8090,debug=True)
