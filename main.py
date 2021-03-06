#!/usr/bin/env python2.7
#coding:utf-8
from flask import session,redirect,url_for,escape
from flask import request
from flask import render_template
from flask import jsonify,abort
from model import db,app,userinfo,event_info,host_info,load_trend,connect_trend,flow_trend,settings
import psutil
import os
import time
import python_jwt as jwt
import datetime
from decimal import Decimal
from functools import wraps
import pandas as pd
import MySQLdb

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=10)

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
    return render_template("tree.html",username=session['username'],id=1)

@app.route('/treedata',methods=['GET'])
@login_required
def treedata():
    id = request.args.get('id')
    host_result=host_info.query.all()
    if len(host_result)==0:
        return jsonify([{"name": u"未发现相关数据"}])
    else: 
        data=[]
        grouplist=set([host.host_group for host in host_result])
        for i in grouplist:
            childreninfo=[{"name":k.description,"id":int(k.id)}  for k in host_result if k.host_group==i]
            for child in childreninfo:
                if int(child['id'])==int(id):
                    child["checked"]="true"
            data.append({"name": i, "open":"true","children":childreninfo})
        return jsonify(data)

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if len(userinfo.query.filter_by(username=request.form['username'],password=request.form['password']).all()) == 0:
            error=u'用户名或密码错误'
            return jsonify({"error":1,"msg":error})
        else:
            #payload = { 'username': request.form['username'] }
            #token = jwt.generate_jwt(payload, app.config["TOKENKEY"], 'PS256', datetime.timedelta(minutes=5))
            session["logged_in"]=True
            session["username"]=request.form['username']
            return jsonify({"error":0,"token":"notused","nexturl":url_for("index")}) 
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

@app.route('/api/rangeinfo',methods=['GET'])
@login_required
def rangeinfo():
    try:
        loadrange=settings.query.filter_by(set_name="loadrange").first()
        memrange=settings.query.filter_by(set_name="memrange").first()
        rootrange=settings.query.filter_by(set_name="rootrange").first()
    except Exception,e:
        return jsonify({"error":1,"msg":str(e)})
    else:
        return jsonify({"error":0,"loadrange":loadrange.set_value,"memrange":memrange.set_value,"rootrange":rootrange.set_value})
    
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
            hostinfodic["hostinfodata"].append({"id":hl.id,"ip":hl.ip,"description":hl.description,"updatetime":str(hl.updatetime),"status":1,"enabled":str(hl.id)+"^"+str(hl.enabled)})
        else:
            hostinfodic["hostinfodata"].append({"id":hl.id,"ip":hl.ip,"description":hl.description,"updatetime":str(hl.updatetime),"status":0,"enabled":str(hl.id)+"^"+str(hl.enabled)})
    return jsonify(hostinfodic)

@app.route('/localinfo',methods=['GET'])
def localinfo():
    try:
        token=request.headers["authkey"]
        #header, claims = jwt.verify_jwt(token, app.config["TOKENKEY"], ['PS256'])
    except Exception,e:
        return jsonify({"error":1,"msg":str(e)})
    else:
        logical_cores=float(psutil.cpu_count())*2
        now_load=float(os.getloadavg()[0])
        loadpercent=now_load/logical_cores*100
        diskpercent=psutil.disk_usage('/').percent
        mempercent=psutil.virtual_memory().percent
        return jsonify({"error":0,"loadpercent":loadpercent,"diskpercent":diskpercent,"mempercent":mempercent})

@app.route('/settings',methods=['GET'])
@login_required
def settingshtml():
    id=request.args.get('method',None)
    templateid="settings-"+id+".html"
    if id == "alarmset":
        times_obj=settings.query.filter_by(set_name="times").first()
        alarmvalue=times_obj.set_value
        return render_template(templateid,username=session['username'],bodytype=id,alarmvalue=alarmvalue) 
    else:
        return render_template(templateid,username=session['username'],bodytype=id) 

@app.route('/api/realtimeinfo',methods=['GET'])
def realtimeinfo():
    id=request.args.get('id',None)
    hostinfo=host_info.query.filter_by(id=id).first()
    if hostinfo: 
        infodict=eval(hostinfo.information)
        diskusage=float([diskitem for diskitem in infodict["disk_info"] if diskitem["mountpoint"]== "/"][0]["percent"])
        memusage=float(infodict["mem_info"]["used"])/float(infodict["mem_info"]["total"])*100
        loadusage=float(infodict["cpu_info"]["load_avg"].split()[0])/float(infodict["cpu_info"]["logical_cores"])*100
        cacheusage=(float(infodict["mem_info"]["cached"])+float(infodict["mem_info"]["buffers"]))/float(infodict["mem_info"]["total"])*100
    else:
        diskusage=0
        memusage=0
        loadusage=0
        cacheusage=0
    return jsonify({"diskusage":float(Decimal(diskusage).quantize(Decimal('0.00'))),"memusage":float(Decimal(memusage).quantize(Decimal('0.00'))),"loadusage":float(Decimal(loadusage).quantize(Decimal('0.00'))),"cacheusage":float(Decimal(cacheusage).quantize(Decimal('0.00')))})

@app.route('/api/trendinfo',methods=['POST'])
def trendinfo():
    etype=request.form.get('etype')
    mysql_cn= MySQLdb.connect(host='localhost', port=3306,user='root', passwd='chinatt_1347', db='lyzto')
    if etype == "loadinfo" or etype == "flowinfo":
        df = pd.read_sql('select * from load_trend;', con=mysql_cn)   
        df.load_value.astype(float)
        datas = df.load_value.values
        dates = df.updatetime.values
        ts=pd.Series(datas,index=dates)
        tsresample=ts.resample('5T',closed="left",label='left').mean().bfill()
        mysql_cn.close()
        return jsonify({"xaix":list(tsresample.index.strftime('%Y-%m-%d %H:%M:%S')),"data":list(tsresample.values)})
    else:
        df = pd.read_sql('select * from connect_trend;', con=mysql_cn)   
        df.establish_value.astype(int)
        datas = df.establish_value.values
        dates = df.updatetime.values
        ts=pd.Series(datas,index=dates,dtype=int)
        tsresample=ts.resample('5T',closed="left",label='left').mean().bfill()
        mysql_cn.close()
        return jsonify({"xaix":list(tsresample.index.strftime('%Y-%m-%d %H:%M:%S')),"data":list(tsresample.values)})
        

@app.route('/logout')
def loginout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return jsonify({"loginurl":url_for("login"),"error":0})

@app.route('/api/changeswitch',methods=['POST'])
def alarmswitch():
    id=request.form.get("hostid",None)
    enabled=request.form.get("state",None)
    if all([id,enabled]):
        try:
            enabled_result=host_info.query.filter_by(id=id).first()
            if enabled=="true":
                enabled_result.enabled=1
            else:
                enabled_result.enabled=0
            db.session.commit()
        except Exception,e:
            return jsonify({"error":1,"msg":str(e)})
        else:
            return jsonify({"error":0,'msg':u'已更改'})
    else:
        return jsonify({"error":1,"msg":"id or enabled is null"})


@app.route('/api/changesettings',methods=['POST'])
def changesettings():
    times=request.form.get("times",None)
    if times:
        try:
            times=int(times)
            tm_result=settings.query.filter_by(set_name="times").all()
            if len(tm_result):
                times_obj=settings.query.filter_by(set_name="times").first()
                times_obj.set_value=times
                db.session.commit()
            else:
                db.session.add(settings(set_name='times',set_value=times))
                db.session.commit()
        except Exception,e:
            return jsonify({"error":1,"msg":"输入不合法"})
        else:
            return jsonify({"error":0,"msg":"修改成功"})
    else:
        return jsonify({"error":1,"msg":"输入不合法"})
        
@app.route('/api/setrange',methods=['POST'])
def setrange():
    rootrange=request.form.get("rootrange",None)
    loadrange=request.form.get("loadrange",None)
    memrange=request.form.get("memrange",None)
    if all([rootrange,loadrange,memrange]):
        try:
            root_obj=settings.query.filter_by(set_name="rootrange").first()
            mem_obj=settings.query.filter_by(set_name="memrange").first()
            load_obj=settings.query.filter_by(set_name="loadrange").first()
            root_obj.set_value=rootrange
            mem_obj.set_value=memrange
            load_obj.set_value=loadrange
            db.session.commit()
        except Exception,e:
            return jsonify({"error":1,"msg":"输入不合法"})
        else:
            return jsonify({"error":0,"msg":"修改成功"})
    else:
        return jsonify({"error":1,"msg":"输入不合法"})

@app.route('/api/posthostinfo',methods=['POST'])
def posthostinfo():
    if request.form.get("host_info",None):
         info_dict=eval(request.form["host_info"])
         ip=info_dict["ip_dict"]['gatewayifaceip']
         description=info_dict["description"]
         try:
             info_result=host_info.query.filter_by(ip=ip).all()
             if len(info_result)==0:
                 db.session.add(host_info(ip=ip,description=description,information=str(info_dict),updatetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                 db.session.add(event_info(ip=ip,information=u"加入监控队列",create_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                 db.session.add(connect_trend(ip=ip,establish_value=info_dict['connect_info']['ESTABLISHED'],listen_value=info_dict['connect_info']['LISTEN'],updatetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                 for key in info_dict['flow_info']['pernic_statis'].keys():
                     db.session.add(flow_trend(ip=ip,iface=key,sent_value=info_dict['flow_info']['pernic_statis'][key]['sent_rate'],recv_value=info_dict['flow_info']['pernic_statis'][key]['recv_rate'],updatetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                 db.session.add(load_trend(ip=ip,load_value=info_dict['cpu_info']['load_avg'].split()[0],updatetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                 db.session.commit()
             else:
                 db.session.add(connect_trend(ip=ip,establish_value=info_dict['connect_info']['ESTABLISHED'],listen_value=info_dict['connect_info']['LISTEN'],updatetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                 for key in info_dict['flow_info']['pernic_statis'].keys():
                     db.session.add(flow_trend(ip=ip,iface=key,sent_value=info_dict['flow_info']['pernic_statis'][key]['sent_rate'],recv_value=info_dict['flow_info']['pernic_statis'][key]['recv_rate'],updatetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                 db.session.add(load_trend(ip=ip,load_value=info_dict['cpu_info']['load_avg'].split()[0],updatetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                 update_sql=host_info.query.filter_by(ip=ip).first()
                 update_sql.information=str(info_dict)
                 update_sql.description=description
                 update_sql.updatetime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                 db.session.commit()
         except Exception,e:
             return jsonify({"error":1,"msg":str(e)})
         else:
             return jsonify({"error":0})
    else:
        return jsonify({"error":1,"msg":"info Incomplete"})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=6666)
