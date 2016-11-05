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
maxRetryTimesForPassword=3
#Configuration area end

#Global status area
debug=False
exit=False
passwordIncorrectTimes =0
isConnected=False
refreshNetwork=False
serverFailureTimes=0
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
			return 
def isSpecifiedWlanAvailable(name):
    '''Check if specified wlan is available to the host.
    Parameter:
             name -- wlan name
    Return value:
             True --Specified wlan is available.
             False -- Specified wlan is not available.
    '''
    p = subprocess.Popen(
        'netsh wlan show networks',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout,stderr=p.communicate()
    if name in stdout:
        return True
    else:
        return False
def isConnectedToSpecifiedWlan(name):
    '''return Ture if host is connected to specified wlan,otherwise return false'''
    p=subbprocess.Popen(
        'netsh wlan show interfaces',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout,stderr=p.communicate()
    if name in stdout:
        return True
    else:
        return False
def ConnectTo(name):
    '''connect to specified wlan.'''
    p=subprocess.Popen(
        'netsh wlan connect{0}'.format(name),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout,stderr =p.communicate()
    if len(stdout)==22 or 'Connection request was complete successfully'in stdout:
        return True
    else:
        return False

def turnOnWifi(ssid,password):
    if len(password)<8:
        cPrint('[ERROR] Password shall contain at least 8 characters',COLOR.DARKRED)
        return False
    p=subprocess.Popen(
        'netsh wlan stop hostnetwork',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout,stderr=p.communicate()

    p=subprocess.Popen(
        'netsh wlan set hostednetwork mode=allow ssid=%s key=%s'%(ssid,password),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout,stderr=p.communicate()

    p=subprocess.Popen(
        'netsh wlan start hostednetwork',
        shell =True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout,stderr=p.communicate()
    return True
def login(username,password):
    '''login wlan using given username and password.'''
    global passwordIncorrectTimes
    global isConnected
    global exit
    data={'action':'login','username':username,'password':password,'ac_id':'20',
          'user_mac':'undefined','save_me':'0','ajax':'1'}
    data=urllib.parse.urlencode(data)
    try:
        req=Request('https://gw.buaa.edu.cn:802/include/auth_action.php')
        binary_data=data.encode()
        response =urlopen(req,binary_data,timeout=10)
        content=response.read()
        response.close()
        if 'help.html' in content:
            passwordIncorrectTimes=0
            isConnected=True
            return True
        else:
            if len(content)==27:
                if passwordIncorrectTimes==3:
                    exit=True
                else:
                    cPrint("[WARNING] Username or password is incorrect.Please check them again.",COLOR.DARKRED)
                    cPrint("[INFO] Retry for {0} more times".format(maxRetryTimesForPassword-passwordIncorrectTimes))
                    passwordIncorrectTimes+=1
            else:
                cPrint('[ERROR]Unknown error'+content.decode('utf-8'))
            return False
        except (URLError,e):
            if hasattr(e,'reason'):
                info='[ERROR]Failed to reach the server.\n reason:'+str(e.reason)
            elif hasattr(e,'code'):
                info='[ERROR]The server couldn\'t fullfill the request\n error code:'+str(e.code)
            else:
                info='[ERROR]Unknown error'
            cPrint(info,COLOR.RED)
            return False
        except Exception:
            import traceback
            print('Generic exception'+traceback.format_exc())
            return False
def cleanLog():
    global refreshNetwork,serverFailureTimes,isConnected,passwordIncorrectTimese
    refreshNetwork=False
    passwordIncorrectTimes=0
    serverFailureTimes=0
    isConnected=False

def refreshNetworkFunc():
    p=subprocess.Popen(
        'netsh wlan disconnect',
        shell =True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout,stderr=p.communicate()
def _ipconfig_getnode():
    ''' Get the hardware address on windows bt runnning ipconfig.exe'''

    def random_getnode():
        ''' Get a random node ID ,with eighth bit set as suggested by RFC4122'''
        import random
        return random.randrange(0,1<<48)

    import os,re
    dirs =['',r'c:\windows\system32',r'c:\winnt\system32']
    try:
        import ctypes
        buffer=ctypes.create_string_buffer(300)
        ctypes.windll.kerne132.GetSystemDirectoryA(buffer,300)
        dirs.insert(0,buffer.value.decode('mbcs'))




    








