from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import  Crypto.PublicKey.RSA as RSA
import json
class MyEncoder(json.JSONEncoder):  
  def default(self, obj):  
      if isinstance(obj, datetime):  
          return obj.strftime('%Y-%m-%d %H:%M:%S')  
      elif isinstance(obj, date):  
          return obj.strftime('%Y-%m-%d')  
      else:  
          return json.JSONEncoder.default(self, obj)
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:chinatt_1347@192.168.111.70:3306/lyzto'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['SECRET_KEY'] = 'jjskdjlkasjdlfjalk'
app.config['TOKENKEY'] = RSA.generate(2048) 
db = SQLAlchemy(app)
manager = Manager(app)
class userinfo(db.Model):
    __tablename__ = 'userinfo'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(320))
    password = db.Column(db.String(320))
    enabled = db.Column(db.Boolean,server_default="1")
    create_time = db.Column(db.DateTime, nullable=False)
    def __repr__(self):
        return json.dumps({"id":self.id,"create_time":self.create_time,"username":self.username,"password":self.password,"enabled":self.enabled},cls=MyEncoder) 
class status_history(db.Model):
    __tablename__ = 'status_history'
    id = db.Column(db.Integer, primary_key=True)
    mid = db.Column(db.String(100))
    item_type=db.Column(db.String(100),server_default="disk")
    last_status = db.Column(db.Boolean, nullable=False)
    alarm_time = db.Column(db.String(100), nullable=True)
    last_alarm_time = db.Column(db.String(100), nullable=True)
    alarm_times = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return json.dumps({"mid":self.mid,"last_status":self.last_status,"alarm_time":self.alarm_time,"alarm_times":self.alarm_times}) 
class host_info(db.Model):
    __tablename__ = 'host_info'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100), unique=True)
    information=db.Column(db.Text(1200))
    host_group=db.Column(db.String(100),server_default="default")
    enabled = db.Column(db.Boolean,server_default="1")
    updatetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return json.dumps({"id":self.id,"ip":self.ip,"infomation":self.information,"enabled":self.enabled,"updatetime":self.updatetime,"description":self.description},cls=MyEncoder) 
class load_trend(db.Model):
    __tablename__ = 'load_trend'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), unique=False)
    load_value = db.Column(db.Float, unique=False)
    updatetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return json.dumps({"id":self.id,"ip":self.ip,"load_value":self.load_value,"updatetime":self.updatetime},cls=MyEncoder) 
class connect_trend(db.Model):
    __tablename__ = 'connect_trend'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), unique=False)
    establish_value = db.Column(db.String(100), unique=False)
    listen_value = db.Column(db.Integer, unique=False)
    updatetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return json.dumps({"id":self.id,"ip":self.ip,"connect_value":self.load_value,"updatetime":self.updatetime},cls=MyEncoder) 
class settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    set_name = db.Column(db.String(100), unique=False)
    set_value = db.Column(db.String(100), unique=False)
    def __repr__(self):
        return json.dumps({"id":self.id,"set_name":self.set_name,"set_value":self.set_value}) 
class flow_trend(db.Model):
    __tablename__ = 'flow_trend'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100), unique=False)
    sent_value = db.Column(db.String(100), unique=False)
    recv_value = db.Column(db.Float, unique=False)
    iface = db.Column(db.String(100), unique=False)
    updatetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return json.dumps({"id":self.id,"ip":self.ip,"iface":self.iface,"flow_value":self.load_value,"updatetime":self.updatetime},cls=MyEncoder) 

class event_info(db.Model):
    __tablename__ = 'event_info'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100))
    information=db.Column(db.String(500))
    create_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return json.dumps({"id":self.id,"ip":self.ip,"infomation":self.information,"create_time":self.create_time},cls=MyEncoder) 
if __name__=="__main__":
    manager.run()
