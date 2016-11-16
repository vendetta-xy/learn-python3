# -*- coding:utf-8 -*-
#
#AUTO_LOGIN_BUAAWIFI and AUTO_START_HOTSPOT
#author: Yang Xiao,BUAA

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
log_name='log'
db_name='pylog.dll'
#Configuration area end

#Global status area
debug=False
exit=False
passwordIncorrectTimes =0
isConnected=False
refreshNetwork=False
serverFailureTimes=0
isAskedTurnOnWifi=False
wifinamePrefix='BUAA-'

DecryptionIdentifier='542916113@qq.com'
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
    except:
        pass
    for dir in dirs:
        try :
            pipe=os.popen(os.path.join(dir,'ipconfig')+'/all')
        except IOError:
            continue
        bestMacAddress ='000000000000'
        for line in pipe:
            value=line.split(':')[-1].strip().lower()
            if re.match('([0-9a-f][0-9a-f]-){5}[0-9a-f][0-9a-f]',value):
                value =value.replace('-','')
                if value.count('0')<bestMacAddress.count('0'):
                    bestMacAddress = value
            if bestMacAddress !='000000000000':
                return bestMacAddress
            else:
                return None
def generateKey():
    import uuid
    import sys
    from binascii import unhexlify as unhex
    if sys.platform=='win32':
        mac =_ipconfig_getnode()
    else:
        print ('can\'t not work on other system ')
    if mac ==None:
        mac=hex(_random_getnode())[2:-1]
    ud=uuid.uuid1()
    ud=ud.hex
    hi_time =ud[12:16]
    key =hi_time +mac
    return unhex(key)

def encrypt(text):
    if isinstance(text,str)==False:
        raise TypeError
    key=generateKey()
    text =DecryptionIdentifier +text
    des = pyDes.des(key,padmode = pyDes.PAD_PKCSS)
    return des.encrypt(text)
def decrypt(cipher):
    key =generateKey()
    des = pyDes.des(key)
    dcyIDLen=len(DecryptionIdentifier)
    text=des.decrypt(cipher,padmode = pyDes.PAD_PKCS5)
    if len(text)< dcyIDLen or text[0:dcyIDLen] !=DecryptionIdentifier:
        raise DecryptionError
    else:
        text =text [dcyIDLen:]
        return text
def delete(db_name):
    if os.path.isfile(db_name):
        os.remove(db_name)
    else:
        cPrint('[ERROR] DB does not exist.',COLOR.RED)

def connectToDB(db_name):
    conn=sqlite3.connect(db_name)
    cu = conn.cursor()
    sqlScript =''' CREATE TABLE IF NOT EXISTS user
               (
               userID INTEGER PRIMARY KEY AUTOINCREMENT,
               userStudentID BLOB NOT NULL UNIQUE ON CONFLICT IGNORE,
               userPassword BLOB NOT NULL
               );
            '''
    try:
        cu.execute(sqlScript)
        conn.commit()
    except sqlite3.DatabaseError as e:
        #DB is damaged.Delete the file and create if again.
        cPrint("[WARNING] Database is weird.Retrieving...",COLOR.DARKRED)
        cu.close()
        deleteDB(db_name)

        conn =sqlite3.connect(db_nmae)
        cu =conn.cursor()
        cu.execute(sqlScript)
        conn.commit()
        cPrint("[INFO] Database is retrieved.",COLOR.SILVER)
    return (conn,cu)
def fetchUserData(conn,cu):
    cu.execute('''SELECT * FROM user''')
    res =cu.fetchone()
    if res ==None:
        return (None, None)
    else:#res[0]= id ,res[1]=student,res[2]=password
        try:
            username=decrypt(res[1])
            password=decrypt(res[2])
        except ValueError as e:
            cPrint("[WARNING] Database is damaged.Retrieving...",COLOR.DARKRED)
            cleanDB(conn,cu)
            username =password=None
        except DecryptionError as e:
            cPrint("[WARNING] Session expires.Please enter username and password again.",COLOR.DARKRED)
            cleanDB(conn,cu)
            username =password=None
        except Exception as e :
            import traceback
            print("Generic exception:" + traceback,format_exc())
        finally:
            return (username,password)

def inputUsernameAndPassword():
    '''get username and password from console
            Retrun value:
                     (isRememberPassword,useranme,password)
    '''

    usernameLength=0
    while usernameLength ==0:
        username = input("Please input your BUAA username:")
        usernameLength =len(username)
    passwordLength =0
    while passwordLength ==0:
        password =input("Please input your BUAA password:")
        passwordLength =len(password)
    state =input("Remember this password on this laptop?(y/n)")
    if state =='Y'or state =='y':
        isRememberPassword =True
    else:
        isRememberPassword =False
    return (isRememberPassword,username,password)

def isUseThisUsername(username):
    '''Ask user whether use the showed username to login.
    Parameter:
             username:
    Return Value:
             True --use this username
             False --do not use this username
    '''
    cPrint("Basterd",color=COLOR.GREEN,mode=1)
    cPrint(" %s "%username ,color=COLOR.BROWN,mode=1)
    cPrint(",is it you?(y/n)",color =COLOR.SILVER,mode=1)
    state =input()
    if state=='Y' or state=='y' or state =='':
        return True
    else:
        return False
def insertUsernameAndPasswordToDB(conn,cu,username,password):
    username=encrypt(username)
    password=encrypt(password)
    #test
    #from binascii import hexlify
    #writeLog(hexlify(generateKey()),'w')
    cu.execute("INSERT INTO user(userStudentID,userPassword)VALUE(?,?)",buffer(username),buffer(password) )
    conn.commit()

def cleanDB(conn,cu):
    query='''DELETE FROM user'''
    cu.execute(query)
    conn.commit()

def isAskedTurnOnWifiFunc():
    return isAskedTurnOnWifi
def isTurnOnWifi():
    global isAskedTurnOnWifi
    isAskedTurnOnWifi =True
    state=input("Do you want to turn on your laptop hotspot?(y/n)")
    if state=='Y' or state=='y':
        return True
    else:
        return False
def inputWifiNameAndPassword():
    global wifinamePrefix
    nameLength =0
    while nameLength ==0:
        wifiName=input("Please set your wifi name(SSID):")
        nameLength =len(wifiname)
    wifiName =wifinamePrefix+wifiName
    passwordLength =0
    while passwordLength<8:
        wifiPassword =input("Please set your wifi password(at least 8 digits):")
        passwordLength=len(wifiPassword)
    return (wifiName,wifiPassword)

def generatePassword(length,mode=None):
    import random
    if isinstance(length,int)==False:
        raise TypeError
    if length<1:
        return None
    seed =uuid.uuid4().int
    password=""
    for x in xrange(0,length):
        #[a-zA-Z0-9 62 characters in total]
        c=random.randint(0,61)
        if c<10:
            password+=chr(c+ord('0'))
        elif c<36:
            password +=chr(c+ord('A')-10)
        else:
            password+=chr(c+ord('a')-36)
    return password


def writeLog(msg,mode ='a'):#'a'是追加模式，从EOF开始，必要时创建新文件
    fp = open(log_name,mode)
    fp.write(msg)
    fp.write('\n')
    fp.close()
def readLog():
    if os.path.isfile(log_name)==True:
        fp = open(log_name,'r')
        msg =fp.read()
        fp.close()
        return msg
    else:
        return ""

def main():
    global exit
    welcomeMsg()
    (conn,cu)=connectToDB(db_name)
    (username,password)=fetchUserData(conn,cu)
    if username !=None:
        if isUseThisUsername(username) ==False:
            #clean DB and input new username and password
            cleanDB(conn,cu)
            username =password =None
    if username ==None:
        (isRememberPassword,username,password)=inputUsernameAndPassword()
        if isRememberPassword==True:
            insertUsernameAndPasswordToDB(conn,cu,username,password)
        else:
            cleanDB(conn,cu)
    cu.close()
    conn.close()





        





    








