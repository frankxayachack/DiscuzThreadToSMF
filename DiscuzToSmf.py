#/usr/bin/python
#__author__ = Sengxay Xayachack

import requests
from bs4 import BeautifulSoup
from requests_login.loginer import Loginer
import re
import hashlib

#initialize
DiscuzDomain = '' # e.g http://discuz.com
SmfDomain = '' # e.g http://smf.com

DisUsername = '' #Discuz Username
DisPassword = '' #Discuz Password

SmfUsername = '' #SMF Username 
SmfPassword = '' #SMF Password

DisLink = raw_input("Source Link (Discuz) : ") # e.g http://discuz.com/forum.php?mod=viewthread&tid=10883
CatID = input('SMF Category ID : ') # e.g 1 or 2 (check in URL)

#Discuz PART

#Login
query = '/member.php?mod=logging&action=login&loginsubmit=yes&inajax=1'
data = dict(loginfield=DisUsername, questionid='0')
cookies = Loginer(query, data)(DiscuzDomain, user=dict(username=DisUsername, password=DisPassword))
if cookies:
	print "Discuz Logged in!"
else:
        print "Discuz Login failed!"
        exit(0)

r = requests.get(DisLink, cookies = cookies)
soup = BeautifulSoup(r.text, 'html.parser')
#END LOGIN

#remove unnecessery information
td = soup.find("td","t_f")
desc = str(td)
desc = desc.split('\n')
desc.pop(0)
desc.pop(-1)
final = '\n'.join(desc)
final = final.replace("file=","src=")

#Content
title = soup.find(id='thread_subject').string
if "pstatus" in final:
        tmp = final.split('<br/>')
        tmp.pop(0)
        tmp.pop(0)
        tmp = ''.join(tmp)
        final = tmp

print title

# END Discuz PART

# ====================================================

# SMF PART

#Initialize

#creat session
s = requests.Session()

#LOGIN TO SMF


uri = "/index.php?action=login"

url = SmfDomain+uri

html = s.get(url).text

#get hash_passwd value
hash_passwd = re.search(r"this, '(.+)'",html)
#print hash_passwd.group(1)

#get 2 hidden fields with random values
hidden = re.findall(r"type=\"hidden\" name=\"(.*?)\" value=\"(.*?)\"",html)
print "hidden name => " + hidden[0][0] + " | hidden value => " + hidden[0][1]

#set Variables
HashPassword = hash_passwd.group(1)
hName = hidden[0][0]
hValue = hidden[0][1]

#encrypt before send to server sha1(sha1(user+pass)+hash_passwd)
hPassword = hashlib.sha1(hashlib.sha1(SmfUsername+SmfPassword).hexdigest()+HashPassword).hexdigest()

#prepare data for sending POST to server
data = {'user':SmfUsername, "passwrd":"", "cookielength":"-1","hash_passwrd":hPassword,hName:hValue}
#print data
r = s.post(SmfDomain+"/index.php?action=login2",data=data)
if SmfUsername in r.text:
    print "SMF Logged in"
else:
    print "SMF Login failed"
    exit(0)

#POST TO SMF
url = SmfDomain+"/index.php?action=post2;start=0;board="+str(CatID)

#get hidden fields
hidden = re.findall(r"type=\"hidden\" name=\"(.*?)\" value=\"(.*?)\"",s.get(url).text)

hFieldName = hidden[-2][0]
hFieldValue = hidden[-2][1]
seqnum = hidden[-1][1]


#prepare data
message = "[html]"+final+"[/html]"

data = {'topic':'0','subject':title,'icon':'xx','sel_face':'','sel_size':'','sel_color':'','message':message,'message_mode':'0','notify':'0','lock':'0','sticky':'0','move':'0','additional_options':'0',hFieldName:hFieldValue,'seqnum':seqnum}

#use Try & Except to intercept unexpected error
try:
        s.post(url,data)
        print "Posted on SMF site"
        exit(0)
except:
        print "Posting failed"
        exit(0)
        