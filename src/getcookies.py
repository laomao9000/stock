import os
import sqlite3
import requests
from win32.win32crypt import CryptUnprotectData
#import win32crypt
 
def getcookiefromchrome(host='.xueqiu.com'):
  cookiepath=os.environ['LOCALAPPDATA']+r"\Google\Chrome\User Data\Default\Cookies"
  sql="select host_key,name,encrypted_value from cookies where host_key='%s'" % host
  with sqlite3.connect(cookiepath) as conn:
    cu=conn.cursor()    
    cookies={name:CryptUnprotectData(encrypted_value)[1].decode() for host_key,name,encrypted_value in cu.execute(sql).fetchall()}
    print(cookies)
    return cookies
 

#getcookiefromchrome()
#getcookiefromchrome('.baidu.com')
 
url='http://www.xueqiu.com/'
 
httphead={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',}


r=requests.get(url,headers=httphead,cookies=getcookiefromchrome('.xueqiu.com'),allow_redirects=1)
print(r.text)