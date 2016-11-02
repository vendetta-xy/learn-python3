import sys
class COLOR:
    BLACK=0
    BLUE=1
    DARKGREEN=2
    DARKCYAN=3
    DARKRED=4
    DARKPINK=5
    BROWN=6
    SILVER=7
    GRAY=8
    BLUE=9
    GREEN=10
    CYAN=11
    RED=12
    PINK=13
    YELLOW=14
    WHITE=15
def cPrint(msg,color =COLOR.BLUE):
    import ctypes
    ctypes.windll.Kernel32.GetStdHandle.restype = ctypes.c_ulong
    h = ctypes.windll.Kernel32.GetStdHandle(ctypes.c_ulong(0xfffffff5))
    if isinstance(color, int) == False or color < 0 or color > 15:  
        color = COLOR.SILVER   
    ctypes.windll.Kernel32.SetConsoleTextAttribute(h, color)  
    print (msg)  
    ctypes.windll.Kernel32.SetConsoleTextAttribute(h, COLOR.SILVER)
cPrint('helloworld',1)
