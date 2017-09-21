#!/usr/bin/env python2.7  
#-*- coding: UTF-8 -*-  
import os, sys, inspect  
 
def script_abspath(frame=inspect.currentframe()):  
    current_dir = os.path.split(os.path.abspath(inspect.getfile( frame )))[0]  
    absdir = os.path.realpath(current_dir)  
    return absdir  
 
 
 
def include_dir(incdir):  
    if incdir not in sys.path:  
        sys.path.insert(0, incdir)  
#get current dir and parent dir 
currentdir = script_abspath()  
parentdir=os.path.dirname(currentdir)
#insert sys.path
include_dir(currentdir)  
include_dir(parentdir)  
