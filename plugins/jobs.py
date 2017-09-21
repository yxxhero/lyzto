#!/usr/bin/env python
#coding:utf-8
import uwsgi
from uwsgidecorators import *
import common
from configobj import ConfigObj
from tools.weixinalarm import weixinalarm
import time
import logging
import urllib
import urllib2
import sys
reload(sys)
sys.setdefaultencoding('utf8')
config=ConfigObj("etc/lyzto.conf",encoding="UTF8")
agentid=config["weixin"]["agentid"]
corpid=config["weixin"]["corpid"]
secrect=config["weixin"]["secrect"]
times_default=int(config["alarm"]["times"])-2
weixinsender=weixinalarm(corpid=corpid,secrect=secrect,agentid=agentid)
import MySQLdb
from DBUtils.PersistentDB import PersistentDB
#mysql连接池类
class MysqlConnectionPool(object):
    __pool = None;
    def __enter__(self):
        self.conn = self.__getConn();
        self.cursor = self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor);
        return self;

    def __getConn(self):
        if self.__pool is None:
            self.__pool = PersistentDB(creator=MySQLdb,host=config["mysql"]["host"],user=config["mysql"]["user"],passwd=config["mysql"]["passwd"],db=config["mysql"]["db"],port=int(config["mysql"]["port"]))

        return self.__pool.connection()

    def __exit__(self, type, value, trace):
        self.cursor.close()
        self.conn.close()

def getMysqlConnection():
    return MysqlConnectionPool()
#获取mysql的值
def getsetvalue(name):
    with getMysqlConnection() as db:
        value_sql="select * from settings where set_name='%s';" %(name)
        db.cursor.execute(value_sql)
        times_result=db.cursor.fetchall()
    return times_result[0]["set_value"]
#日志模式初始化
logging.basicConfig(level="DEBUG",
                format='%(asctime)s  %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                filename='log/lyzto.log',
                filemode='a')
def alarmpolicy(mid,des,itemtype):
    with getMysqlConnection() as db:
        sql="select * from status_history where mid='%s' and item_type='%s';" %(str(mid),itemtype)
        db.cursor.execute(sql)
        status_info=db.cursor.fetchall()
        if len(status_info):
            try:
                times=int(getsetvalue(name="times"))-2
            except Exception,e:
                logging.error(str(e))
                times=int(times_default)-2
            else:
                pass
            if int(time.time())- round(float(status_info[0]["alarm_time"]))<= 3600 and int(status_info[0]["alarm_times"]) <= times:
                if int(status_info[0]["alarm_times"]) == times:
                    weixinsender.sendmsg(title=itemtype+"(当前时间最后一次报警)",description=des)
                else:
                    weixinsender.sendmsg(title=itemtype,description=des)
                count=int(status_info[0]["alarm_times"])+1
                if int(status_info[0]["alarm_times"])==0:
                    update_sql = "UPDATE status_history SET alarm_time='%s' ,alarm_times = '%d' , last_alarm_time= '%s',last_status = '%d' WHERE mid = '%s' and item_type= '%s'" % (str(time.time()),count,str(time.time()),0,mid,itemtype)
                else:
                    update_sql = "UPDATE status_history SET alarm_times = '%d' , last_alarm_time= '%s',last_status = '%d' WHERE mid = '%s' and item_type='%s'" % (count,str(time.time()),0,mid,itemtype)
                with getMysqlConnection() as db:
                    try:
                        db.cursor.execute(update_sql)  
                        db.conn.commit()
                    except Exception,e:
                        logging.error("'%s' type('%s') 数据更新异常:'%s'" %(mid,itemtype,str(e)))
                    else:
                        logging.info("'%s' type('%s') 数据更新成功" %(mid,itemtype))
            elif int(time.time())- round(float(status_info[0]["alarm_time"]))<= 3600 and int(status_info[0]["alarm_times"]) > times:
                logging.info("'%s':报警次数已达上限('%s')" %(mid,itemtype)) 
            elif time.time()- round(float(status_info[0]["alarm_time"]))> 3600:
                weixinsender.sendmsg(title=itemtype,description=des)
                update_sql = "UPDATE status_history SET alarm_times = '%d',alarm_time='%d' ,alarm_time='%s',last_status = '%d' WHERE mid = '%s' and item_type = '%s' " % (0,time.time(),str(time.time()),0,mid,itemtype)
                with getMysqlConnection() as db:
                    try:
                       db.cursor.execute(update_sql) 
                       db.conn.commit()
                    except Exception,e:
                        logging.error(str(e))
                        logging.error("'%s' type('%s') 数据更新异常:'%s'" %(mid,itemtype,str(e)))
                    else:
                        logging.info("'%s' type('%s') 数据更新成功" %(mid,itemtype))
        else:
            weixinsender.sendmsg(title=itemtype,description=des)
            update_sql = "INSERT INTO status_history (mid,last_status,alarm_time,last_alarm_time,alarm_times,item_type) VALUES ('%s','%d','%s','%s','%d','%s')" % (mid,0,str(time.time()),str(time.time()),0,itemtype)
            with getMysqlConnection() as db:
                try:
                   db.cursor.execute(update_sql) 
                   db.conn.commit()
                except Exception,e:
                    logging.error(str(e))
                    logging.error("'%s' type('%s') 数据更新异常:'%s'" %(mid,itemtype,str(e)))
                else:
                    logging.info("'%s' type('%s') 数据更新成功" %(mid,itemtype))
def stamp2str(secs):
    m,s = divmod(int(secs), 60)
    h, m = divmod(m, 60)
    return h,m,s
         
def checkstatus(mid,itemtype):
    with getMysqlConnection() as db:
        sql="select * from status_history where mid='%s' and item_type='%s';" %(str(mid),itemtype)
        db.cursor.execute(sql)
        check_info=db.cursor.fetchall()
        if len(check_info):
            if int(check_info[0]["last_status"])==0:
                timerange=int(time.time())-round(float(check_info[0]["alarm_time"]))
                hours,minutes,sec=stamp2str(timerange)
                timedesc=str(hours)+"小时"+str(minutes)+"分"+str(sec)+"秒"
                weixinsender.sendmsg(title=itemtype+"(恢复通知)",description=mid+"已从异常中恢复,异常持续时间:"+str(timedesc))  
                update_sql = "UPDATE status_history SET last_status = '%d' , alarm_times='%d' WHERE mid = '%s' and item_type= '%s'" % (1,0,mid,itemtype)
                with getMysqlConnection() as db:
                    try:
                       db.cursor.execute(update_sql) 
                       db.conn.commit()
                    except Exception,e:
                        logging.error(str(e))
                        logging.error("'%s' 数据更新异常:'%s'" %(mid,str(e)))
                    else:
                        logging.info("'%s' 数据更新成功'" %(mid))
            else:
                logging.info(mid+" :状态未发生异常")
        else:
            logging.info(mid+"("+itemtype+")"+" :状态未发生异常")
            
            
    
@timer(5)
def checkdisk(arg):
    rootrange=float(getsetvalue(name="rootrange"))
    with getMysqlConnection() as db:
        sql="select * from host_info;"
        db.cursor.execute(sql)
        disk_list=db.cursor.fetchall()
        if len(disk_list):
            for diskinfo in disk_list:
                infodict=eval(diskinfo["information"])
                rootusage=float([diskitem for diskitem in infodict["disk_info"] if diskitem["mountpoint"]== "/"][0]["percent"])
                if rootusage >= rootrange:
                    des='根分区已使用'+str(rootusage)+'%,及时清理('+str(diskinfo["description"])+')'
                    logging.info(des)
                else:
                    logging.info("磁盘检测正常")
                    checkstatus(str(diskinfo["description"]),"disk")
                    continue 
                if diskinfo["enabled"]:
                    alarmpolicy(diskinfo["description"],des,"disk")
                else:
                    logging.info(diskinfo["description"]+" 未启用报警")
        else:
            logging.info("未发现disk相关数据")

@timer(3)
def checkmem(arg):
    memrange=float(getsetvalue(name="memrange"))
    with getMysqlConnection() as db:
        sql="select * from host_info;"
        db.cursor.execute(sql)
        mem_list=db.cursor.fetchall()
        if len(mem_list):
            for meminfo in mem_list:
                infodict=eval(meminfo["information"])
                if float(infodict["mem_info"]["used"])/float(infodict["mem_info"]["total"])*100 > memrange:
                    des='内存大于'+str(memrange)+'%,及时处理('+str(meminfo["description"])+')'
                    logging.info(des)
                else:
                    logging.info("内存检测正常")
                    checkstatus(str(meminfo["description"]),"mem")
                    continue 
                if meminfo["enabled"]:
                    alarmpolicy(meminfo["description"],des,"mem")
                else:
                    logging.info(meminfo["description"]+" 未启用报警")
        else:
            logging.info("未发现mem相关数据")

@timer(300)
def checkload(arg):
    loadrange=float(getsetvalue(name="memrange"))
    with getMysqlConnection() as db:
        sql="select * from host_info;"
        db.cursor.execute(sql)
        load_list=db.cursor.fetchall()
        if len(load_list):
            for loadinfo in load_list:
                infodict=eval(loadinfo["information"])
                if float(infodict["cpu_info"]["load_avg"].split()[0]) / float(infodict["cpu_info"]["logical_cores"]) / 1.5 * 100 > loadrange:
                    des='负载过高，及时处理('+str(loadinfo["description"])+')'+' value:'+str(infodict["cpu_info"]["load_avg"].split()[0])
                    logging.info(des)
                else:
                    logging.info("负载检测正常")
                    checkstatus(str(loadinfo["description"]),"load")
                    continue 
                if loadinfo["enabled"]:
                    alarmpolicy(loadinfo["description"],des,"load")
                else:
                    logging.info(loadinfo["description"]+" 未启用报警")
        else:
            logging.info("未发现load相关数据")

@timer(10)
def checkprocesslist(arg):
    with getMysqlConnection() as db:
        sql="select * from host_info;"
        db.cursor.execute(sql)
        proc_list=db.cursor.fetchall()
        if len(proc_list):
            for procinfo in proc_list:
                infodict=eval(procinfo["information"])
                processmonit=set(infodict["keyprocess"])-set(infodict["processlist"])
                if len(processmonit) > 0:
                    proclist=",".join(processmonit) 
                    des=proclist+'进程不存在:'+'('+str(procinfo["description"])+')'
                    logging.info(des)
                else:
                    logging.info("进程检测正常")
                    checkstatus(str(procinfo["description"]),"proc")
                    continue 
                if procinfo["enabled"]:
                    alarmpolicy(procinfo["description"],des,"proc")
                else:
                    logging.info(procinfo["description"]+" 未启用报警")
        else:
            logging.info("未发现进程相关数据")

@timer(5)
def checkreport(arg):
    with getMysqlConnection() as db:
        sql="select * from host_info;"
        db.cursor.execute(sql)
        repo_list=db.cursor.fetchall()
        if len(repo_list):
            for repoinfo in repo_list:
                if abs(time.time() - time.mktime(time.strptime(str(repoinfo["updatetime"]),"%Y-%m-%d %H:%M:%S"))) > 300:
                    des='上报超时('+str(repoinfo["description"])+')'
                    logging.error(des)
                else:
                    checkstatus(repoinfo["description"],"report")
                    continue
                if repoinfo["enabled"]:
                    alarmpolicy(repoinfo["description"],des,"report")
                else:
                    logging.info(repoinfo["description"]+" 未启用报警")
        else:
            logging.info("未发现report相关数据")

@filemon("/opt/lyzto/plugins/jobs.py")
def monitor_py(num):
    logging.info("jobs.py has been modified,reboot")
    uwsgi.reload()

@filemon("/opt/lyzto/main.py")
def monitor_py(num):
    logging.info("main.py has been modified,reboot")
    uwsgi.reload()

@filemon("/opt/lyzto/etc/lyzto.conf")
def monitor_py(num):
    logging.info("configfile has been modified,reboot")
    uwsgi.reload()
