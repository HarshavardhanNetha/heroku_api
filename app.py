from flask import Flask, request
from datetime import date
from datetime import datetime
from time import sleep
import requests
from bs4 import BeautifulSoup as bs
import pytz
import json
import _thread
import random
import urllib.parse

app=Flask(__name__)
@app.route('/')
def hello():
    #f=open("logs_all/logs_all_{}.txt".format(date.today()),"a")
    note="<h4>Thanks for using ~Harsha :)</h4><p>I don't save your passwords. DATA IS WEALTH.</p><h7>Queries or issues? Reach me out <a href=\"https://www.linkedin.com/in/harsha-netha\">here</a></h7>"
    IST = pytz.timezone('Asia/Kolkata') 
    now = datetime.now(IST)
    current_time = now.strftime("%H:%M:%S")

    param1=str(request.args.get('id',default=""))
    param2=str(request.args.get('pwd',default=""))
    code=str(request.args.get('code',default=""))

    if(param1=="" or param2==""):
        return "Login Id/Password Error.<html><h7>You might have forgotten to enter parameters in the url</h7><p>{}</p></html>".format(note)

    headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
    login_data={'username': param1, 'password': param2}

    with requests.Session() as s:
        url="http://lms.rgukt.ac.in/login/index.php"
        try:
            r = s.get(url,headers=headers,timeout=10)
        except:
            return "Timeout Error - Issue with LMS. Check the status of lms.rgukt.ac.in manually."
        if (r.status_code != 200):
            res=f"Server Error {current_time} {param1}\n"
            print(res)
            #f.write(res)
            return f"{res} {note}"

        soup=bs(r.content,'html5lib')
        login_data['logintoken']=soup.find('input', attrs={'name':'logintoken'})['value']
        r = s.post(url,headers=headers,data=login_data)

        if (r.status_code != 200):
            print("Error")
            res=f"Server Error - LoginPage {current_time} {param1}\n"
            #f.write(res)
            return f"{res} {note}"
        
        soup=bs(r.content,'html5lib')
        #id/pwd error
        id_pwd_check=soup.find('title').contents[0]
        if(id_pwd_check!="Dashboard"):
            print("ID/Password Error")
            res=f"ID/Password Error {current_time} {param1}\n"
            #f.write(res)
            return f"{res} {note}"

        sub_link_pre='http://lms.rgukt.ac.in/mod/attendance/view.php?id='
        sub_links=code
        
        url=sub_link_pre+sub_links
        print(url)
        
        r = s.get(url,headers=headers)

        if (r.status_code != 200):
            print("Error")
            res=f"Server Error - AttendancePage {current_time} {param1}\n"
            #f.write(res)
            return f"{res} {note}"
            
        soup=bs(r.content,'html5lib')
        user_name=soup.find('a', attrs={'title':'View profile'}).contents[0]

        check=soup.findAll('td', attrs={'class':'statuscol cell c2 lastcol'})
        if(len(check)==0):
            print("Time Error")
            res=f"Come back on currect time {current_time} {user_name}\n"
            #f.write(res)
            return f"{res} {note}"

        for x in check:
            print(x.find('a')['href'])
            url=x.find('a')['href']
            #print(url)
            print(x.find('a').contents[0])
        r = s.get(url,headers=headers)

        if (r.status_code != 200):
            print("Time Error")
            res=f"Attendance Block Error {current_time} {user_name}\n"
            #f.write(res)
            return f"{res} {note}"

        soup=bs(r.content,'html5lib')
        attnd_data={
            '_qf__mod_attendance_form_studentattendance': '1',
            'mform_isexpanded_id_session': '1',
            'submitbutton': 'Save changes'
        }

        attnd_data['sessid']=soup.find('input', attrs={'name':'sessid'})['value']
        attnd_data['sesskey']=soup.find('input', attrs={'name':'sesskey'})['value']
        values=soup.findAll('input', attrs={'name':'status'})
        attnd_data['status']=values[0]['value']

        url = 'http://lms.rgukt.ac.in/mod/attendance/attendance.php'

        r = s.post(url,headers=headers,data=attnd_data)

        if (r.status_code != 200):
            #print("Error")
            #print("Time Error")
            res=f"Error while submission! {current_time} {user_name}\n"
            #f.write(res)
            return f"{res} {note}"

        print("Attendance submitted successfully!")
        res=f"Attendance SUbmitted Successfully! {current_time} {user_name}\n"
        #f.write(res)
        #f.close()

        return f"{res} {note}"
#extra route which creates cron jobs at ease - works only for cs
@app.route("/cs")
def createAll():
    id_num=urllib.parse.unquote(str(request.args.get('id',default="n")))
    passwrd=urllib.parse.unquote(str(request.args.get('pwd',default="n")))
    param1=urllib.parse.unquote(str(request.args.get('cron',default="n")))
    param2=urllib.parse.unquote(str(request.args.get('job',default="n")))

    
    
    #return urllib.parse.unquote(id_num+passwrd+param1+param2)
    
    
    
    headers={"user-agent":"Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"\
             ,"x-api-method":'Login','X-UI-Language': 'en','Content-Type': 'application/json', 'Accept': 'text/plain',}
    login_data={'email':param1, 'password': param2}
    print(login_data)

    url="https://api.cron-job.org/"
    #password failure request handled
    try:
        r = requests.post(url,headers=headers,timeout=10,data=json.dumps(login_data))
        key=r.json()
    except:
        return "ID/Password error of cron-job.org"
    
    
    api_key=key["token"]
    print(api_key)

    true="true"
    false="false"

    #inputs = id hub-pwd password cronjob email cronjob pwd

    num1=random.randint(5,15)
    num2=random.randint(15,30)
    num3=random.randint(30,45)
    num4=random.randint(45,59)

    class subject:
        def __init__(self,name,code,hr):
            self.name=name
            self.code=code
            self.hr=hr
            data={"job":{"title":self.name,"url":"https://moodle-boy.herokuapp.com/?id={}&pwd={}&code={}".format(id_num,passwrd,self.code),"enabled":true,"saveResponses":true,"auth":{"enable":false,"user":"","password":""},"notification":{"onSuccess":true,"onDisable":true,"onFailure":false},"requestMethod":0,"extendedData":{"body":"","headers":{}},"schedule":{"mdays":[-1],"wdays":[1,2,3,4,5,6],"months":[-1],"hours":[self.hr],"minutes":[num1,num2,num3,num4],"timezone":"Asia/Kolkata"}}}
            self.data=data
            #print(data)
            
            
        def post(self):            
            headers["x-api-method"]="CreateJob"
            headers["Authorization"]="Bearer {}".format(api_key)                
            r = requests.post(url,headers=headers,data=json.dumps(self.data),timeout=5)
            try:
                job_id=r.json()
                print("Succeded loop",job_id,"\n")
                return job_id["jobId"]
            except:
                print(r.status_code,self.name)
                #print("text:",r.text,"content:",r.content,"\n")
                return f"Failed posting {self.name}"
    sleep(3)
    sub1=subject("ES",9488,2)
    sub2=subject("DBMS",9450,9)
    sub3=subject("DA",8773,11)
    sub4=subject("COA",8752,9)
    sub5=subject("MEFA",9328,2)
    sub6=subject("ES_2",9488,6)
    
    sub_list = [sub1,sub2,sub3,sub4,sub5,sub6]
    def new_thread():
        res="<br>"
        for i in sub_list:
            sleep(4)
            res+=i.name+"    "+str(i.post())+"<br>"
            sleep(4)

        return f"You're work is successful dear {id_num} <br> Job IDs: {res}"
    try:
        _thread.start_new_thread( new_thread, () )
        return "Processing request - Logged in Successfully Check your <a href='https://console.cron-job.org/jobs'>dashboard</a> in cron-job website"
    except:
        return "Error starting new_thread. Contact support."

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="4000",debug=True)
