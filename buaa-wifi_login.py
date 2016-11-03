import urllib
from urllib.request import Request,urlopen
from urllib.error import URLError
from colorprint import cPrint
from urllib.parse import urlencode,urlparse
passwordIncorrectTimes=0
isConnected=False
exit=0
def login(username,password):
    '''login wlan using given username and password.'''
    global passwordIncorrectTimes
    global isConnected
    global exit
    data={'action':'login','username':username,'password':password,'ac_id':'20',
          'user_mac':'undefined','save_me':'0','ajax':'1'}
    data=urlencode(data)
    try:
        req=Request('https://gw.buaa.edu.cn:802/include/auth_action.php')
        binary_data=data.encode()
        response =urlopen(req,binary_data,timeout=10)
        content=response.read()
        content=content.decode()
        response.close()
        if 'login_ok' in content:
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
    except URLError as e:
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
if login('15231048','03030319'):
        cPrint ('LOGIN SUCCESSFULLY')
