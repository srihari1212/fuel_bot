import smtplib
import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date, timedelta
import pyrebase
from firebase_config import config
from fuctionalities import conv_str_date,find_between_dates
from data import city_lst
import pandas as pd
from fuctionalities import predict_next
from datetime import datetime
from fuctionalities import conv_str_date,find_between_dates,predict_next
from data import city_lst

sched = BlockingScheduler()

@sched.scheduled_job('interval', hours = 10)
def initiate():
    now = datetime.now()
    today = date.today()
    current_time = now.strftime("%H:%M:%S")
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    e_data =db.get().val()
    startdate = conv_str_date('2021-03-30')
    today = date.today()
    yesterday = today - timedelta(days = 1)
    date_lst = find_between_dates(startdate,today)
    def mailing():
        email = "sriharivenkatesan10488@gmail.com"
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        import smtplib
        s = smtplib.SMTP('smtp.gmail.com', 587) 
        s.ehlo()
        s.starttls() 
        s.ehlo()
        s.login("frontyard2020@gmail.com", "20frontyard20")
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Update from Fuel analyzer'
        msg['From'] = "frontyard2020@gmail.com"
        msg['To'] = email
        body = result_string
        body = MIMEText(body,'html')
        msg.attach(body) 
        s.sendmail("frontyard2020@gmail.com", email, msg.as_string()) 
        s.quit()
        msg="check the mail"
        return "success"
    def gen_df_lst():
        df_lst=[]
        for city in city_lst:
            diesel = []
            petrol = []
            lpg = []
            for date in date_lst:
                diesel.append(float(e_data[date][city]['diesel'].replace('₹','')))
                petrol.append(float(e_data[date][city]['petrol'].replace('₹','')))
                if len (list(e_data[date][city])) == 3:
                    lpg.append(float(e_data[date][city]['lpg'].replace('₹',''))) 
                else:
                    lpg.append(float(0))
            data2df = {'date':date_lst,
                    'diesel':diesel,
                    'petrol':petrol,
                    'lpg':lpg}
                    
            df = pd.DataFrame(data2df)
            df_lst.append(df)
            return df_lst


        # return nxt_petrol,nxt_diesel,nxt_lpg

    def check_for_change(city):
        daily_diff_diesel = round(float(e_data[str(yesterday)][city]['diesel'].replace('₹',''))-float(e_data[str(today)][city]['diesel'].replace('₹','')),4)
        
        daily_diff_petrol = round(float(e_data[str(yesterday)][city]['petrol'].replace('₹',''))-float(e_data[str(today)][city]['petrol'].replace('₹','')),4)
    
        daily_diff_lpg = round(float(e_data[str(yesterday)][city]['lpg'].replace('₹',''))-float(e_data[str(today)][city]['lpg'].replace('₹','')),4)
        if daily_diff_diesel > 0 or daily_diff_petrol > 0 or daily_diff_lpg  > 0:
            return {city:[daily_diff_diesel,daily_diff_petrol,daily_diff_lpg]}
        else:
            return 0

    def result_changes():
        changes_found = []
        for city in city_lst:
            if check_for_change(city) != 0:
                changes_found.append(check_for_change(city))
        return(changes_found)

    def get_res_dailychange():
        new = {}
        category = ['diesel','petrol','LPG']
        new['category']=category
        check = '''     -------------------{}----------------<br>'''.format(category)
        for i in range(0,len(result_changes())):
            check =check+'''<br>
            {}     {}<br>
            -------------------------------------------------------------------------<br>
            '''.format(list(result_changes()[i].keys())[0],list(result_changes()[i].values())[0])
        #print(check)
        #df = pd.DataFrame(new)
        res = check
        return(res)
    nxt_petrol = predict_next(gen_df_lst()[0],'petrol').to_string().split()[1]
    nxt_diesel = predict_next(gen_df_lst()[0],'diesel').to_string().split()[1]
    nxt_lpg = predict_next(gen_df_lst()[0],'lpg').to_string().split()[1]
    result_string = '''{}<br><br>
    Tomorrow's petrol price will be : {}<br>
    Tomorrow's diesel price will be : {}<br>
    Tomorrow's LPG price will be : {}'''.format(get_res_dailychange(),
    nxt_petrol,
    nxt_diesel,
    nxt_lpg)




    mailing()
    print('success '+current_time+" "+str(today))

sched.start()
