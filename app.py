from flask import Flask, request
from datetime import date
from datetime import datetime
from time import sleep
import requests
from bs4 import BeautifulSoup as bs
import pytz 

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
        r = s.get(url,headers=headers)

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

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="4000",debug=True)
