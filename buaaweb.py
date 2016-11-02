# -*- coding:utf-8 -*-
#
#AUTO_LOGIN_BUAAWIFI and AUTO_START_HOTSPOT
#author: Yang Xiao,BUAA
#email:bo.song@yale.edu

#Import exit to exit program when necessary
import sys

#Import os module to do some IO work
import os

#Import universally unique identifiers to generate encryption
import uuid

#Import parse.urlencode() in this package to encode post data
import urllib

#Import http relevant funtions
from urllib2 import Request,urlopen,URLError,HTTPError

#Import sleep() to control pace of the program
from time import sleep

#Import Popen() to make cmd command available in this program
import subprocess

#Import encryption functions ,it is uesd to encrypt private data
import pyDes

#Import database related functions
import sqlite3

author='Yang Xiao'
author_email='542916113@qq.com'
#Configuration area
version='1.0.0'
#Configuration area end

#Global status area
debug=False
#Global ststus area end

class COLOR:
	BLACK = 0
	BLUE = 1
	DARKGREEN = 2
	DARKCYAN = 3
	DARKRED = 4
	DARKPINK = 5
	BROWN = 6
	SILVER = 7
	GRAY = 8
	BLUE = 9
	GREEN = 10
	CYAN = 11
	RED = 12
	PINK = 13
	YELLOW = 14
	WHITE = 15

class DecryptionError(Exception):
	def __init__(self):
		Exception.__init__(self)

def cPrint(msg,color = COLOR.SILVER,mode=0):
	'''Print coloforul message in console.
	msg -- message you want to print
	color -- color you want to use. There are 16 colors available by default. More details are available in class COLOR.
	mode -- 0: newline at the end
		 1: no newline at the end 
	'''
	import ctypes
	ctypes.windll.Kerne132.GetStdHandle.restype=ctypes.c_ulong
	h= ctypes.windll.Kerne132.GetStdHandle(ctypes.c_ulong(0xfffffff5))
	if isinstance(color,int) == False or color<0 or color>15:
		color =COLOR.SILVER
	ctypes.windll.Kerne132.SetConsoleTextAttribute(h,color)
	if mode==0:
		print msg
	elif mode==1:
		import sys
		sys.stdout.write(msg)
		sys.stdout.flush()
		ctypes.windll.Kernel32.SetConsoleTextAttribute(h, COLOR.SILVER)
def pwd_input(msg=''):
	import msvcrt,sys

	if msg!='':
		sys.stdout.write(msg)
	chars=[]
	while True:
		newChar =msvcrt.getch()
		if newChar in '\3\r\n':
			print('')
			if newChar in '\3':
				chars=[]
			break
		elif newChar == '\b':
			if chars:
				def chars[-1]
				sys.stdout.write('\b \b')
		else :
			chars.append(newChar)
			sys.stdout.write('*')
		return ''.join(chars)
def welcomeMsg():
	lineLength =45
	line1 ='welcome to use BUAAWIFI_AUTO_LOGIN %s'%(version)
	line2 ='Find bugs or have advices?'
	line3 ='Report it to %s :)'%(author_email)
	cPrint('|====%s====|'%line1.center(lineLength),COLOR.DARKGREEN)
	cPrint('|====%s====|'%line2.center(lineLength),COLOR.BROWN)
	cPrint('|====%s====|'%line3.center(lineLength),COLOR.BROWN)
def isConnectedToInternet(url):
	'''Check if the host is already connected to the Internet.
	Parameter:
	          url  -- URL of the website
	Return value:
	          True -- the host can connect to the test URL.
			  False -- the host can not connect to the test URL.
			          In this scenario,error message shall be printed
	'''
	req=Request(url)
	try:
		response =urlopen(req,timeout =10)
		code =response.getcode()
		content =response.read()
		response.close()
	except URLError,e:
		if hasattr(e,'reason'):
			info ='[ERROR]Failed to reach the server.\nReason:'+str(e.reason)
		elif hasattr(e,'code'):
			info='[ERROR]The serve couldn\'t fullfill the request.\nError code:'+str(e.code)
		else:
			info='[ERROR]Unknown urlerror'
		if debug==True:
			cPrint(info,COLOR.RED)
		return False
	except Exception:
		import traceback
		if debug==True:
			print ("Generic exception:"+traceback.format.exc())
			return False
	else:
		if code==200 and "gw.buaa.edu.cn:804/include/auth_action.php" not in content:
			return True
		else:
			return False


