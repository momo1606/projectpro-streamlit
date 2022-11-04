from typing import Dict
import pymongo
from pymongo import MongoClient
import pandas as pd
import smtplib
import creds

import warnings
warnings.filterwarnings("ignore")

client = pymongo.MongoClient(
    "mongodb+srv://projectpro:dezyre123@cluster0.etvm5.mongodb.net/?retryWrites=true&w=majority")
db = client["Customers"]
#
# # x=collection.count_documents({})
# # print(x)
# # p={"_id":"kedar@projectpro.io"}
# # #collection.insert_one
# db['sessions'].delete_many({})
#

def get_enroll_data(emails):
    collection4=db["emails"]

    h=collection4.aggregate(
    [
        {"$match":{'email':{"$in":emails}}},
        
        { "$addFields": {
        "converted_start_date": {
        "$dateFromString": {
            "dateString": "$current_period_start",
            "format":"%Y-%m-%d"
        }
        }
    }},

        { '$sort': { 'email': 1, 'converted_start_date': 1 } },
        {
        '$group':
            {
            '_id': "$email",
            'last_Start_Date': { '$last': "$current_period_start" },
            'last_Amount_Paid_by_Customer': {'$last': "$amount"},
            'Join_Date': { '$first': "$date_joined" },
            'country': {'$last': "$country"}
            }
        }
    ]
    )

    return(list(h))



def get_session_counts(emails):

    collection2=db["sessions"]

    cout=collection2.aggregate([
    {"$match":{'Email':{"$in":emails}}},
    {
    "$group":{
        "_id":"$Email",
        "total_sessions":{"$sum":1},
    }
    }
    ])

    return(list(cout))


def get_engage_stats(emails):

    collection3=db["engage_lab_data"]

    l=collection3.aggregate([{
    "$match":{"email":{"$in":emails}}},
   {
        "$group":{
        "_id":{
            "Email":"$email",
            "proj":"$project_id"
            },
         "total_count":{"$sum":1},
         "lab_view":{"$sum":{
             "$cond": [ { "$eq": [ "$Category", "Lab" ] }, "$view_time", 0 ]
         }},
         "watch_time":{"$sum":{
             "$cond": [ { "$eq": [ "$Category", "Engagement" ] }, "$view_time", 0 ]
         }}
    }
    },
    { "$group": {
        "_id": "$_id.Email",
        "totalCount": { "$sum": "$total_count" },
        "Distinct_Projects_Count": { "$sum": 1 },
        "total_lab":{"$sum":"$lab_view"},
        "total_watch":{"$sum":"$watch_time"},
    }},
    {
        "$project":{
            "totalCount":"$totalCount",
            "Distinct_Projects_Count":"$Distinct_Projects_Count",
            "total_lab":"$total_lab",
            "total_watch":"$total_watch",
            'totalSum' : { '$add' : [ '$total_lab', '$total_watch' ] }
        }
    }
    ])

    return(list(l))

def check_email(email):
    collection = db["emails"]
    r = collection.find({})
    for i in r:
        if (i["email"] == email["_id"]):
            return True
    return False



def insert_email(email):
    collection = db["emails"]
    collection.insert_one(email)
    return True



def fetch_emails():
    collection = db["emails"]
    r = collection.find({})
    emails = []
    return ([i["email"] for i in r])


def fetch_refund_emails():
    collection = db["onboard_refund"]
    r = collection.find({})
    emails = []
    refund_list=[i["Email"] for i in r]
    enroll_list=fetch_emails()
    return(list(set(enroll_list) & set(refund_list)))

def fetch_refund_process_emails():
    collection = db["onboard_refund"]
    e=fetch_payment_modes()
    e.remove("Stripe")

    c=list(collection.find({"Status": {"$in":["Partial refund to be processed","Refund in Progress","Retained with Partial Refund","Complete Refund to be processed"]},"Mode":{"$ne":"Stripe"},"Conversation_Grade":"Final response","Amount_Refunded":None}))
    
    refund_list=[i["Email"] for i in c]
    enroll_list=fetch_emails()
    return(list(set(enroll_list) & set(refund_list)))


def fetch_payment_modes():
    collection = db["payment_mode"]
    r = collection.find({})
    emails = []
    return ([i["Mode"] for i in r])

def fetch_payment_currencies():
    collection = db["payment_currency"]
    r = collection.find({})
    emails = []
    return ([i["currency"] for i in r])

def insert_session(session):
    collection = db["sessions"]
    collection.insert_one(session)
    return


def fetch_project_titles():
    db2 = client["Projects"]
    collection = db2["ProjectDetails"]
    r = collection.find({})
    titles = []
    return ([i["Title"] for i in r])



def get_project_id(title):
    db2 = client["Projects"]
    collection = db2["ProjectDetails"]
    x = collection.find_one({"Title": title})
    return (x["_id"])



def get_customer_details(email):
    collection = db["sessions"]
    bool = check_email({"_id": str(email)})
    if collection.find_one({'Email':email})==None:
        return pd.DataFrame()
    elif (bool):
        details = collection.find({"Email": str(email)})
        l = []
        # print(details[0])
        # print(json.dumps(details,indent=4))
        for i in details:
            #print(i)
            l.append(i)
        df=pd.DataFrame.from_records(l).drop('_id',axis=1)
        df['Project_ID']=df['Project_ID'].astype(str)
        return df
    else:
        return pd.DataFrame()

def get_expert_sessions(email):
    collection = db["sessions"]
    if collection.find_one({'Expert_Email':email})==None:
        return pd.DataFrame()
    else:
        details = collection.find({"Expert_Email": str(email)})
 
        df=pd.DataFrame.from_records(list(details)).drop('_id',axis=1)
        df['Project_ID']=df['Project_ID'].astype(str)
        df['Date_of_Session']=pd.to_datetime(df.Date_of_Session,format="%Y-%m-%d", errors='coerce')
        df.sort_values(by='Date_of_Session', inplace=True)
        df.rename(columns = {'Email':'Customer_Email'}, inplace = True)
        if('duration_of_call' in df.columns):
            df2=df[['Name_of_Expert','Date_of_Session','Time_of_Session','duration_of_call','Domain_query','Customer_Email','Session_Completed','session_status']]
        else:
            df2=df[['Name_of_Expert','Date_of_Session','Time_of_Session','Domain_query','Customer_Email','Session_Completed','session_status']]
        #df2=df[['Name_of_Expert','Date_of_Session','Time_of_Session','Domain_query','Customer_Email','Session_Completed','session_status']]
        return df2

def get_renewals_customer(email):
    collection = db["renewals"]
    if collection.find_one({'Email':email})==None:
        return pd.DataFrame()
    else:
        details=collection.find({'Email':str(email)})

        df=pd.DataFrame.from_records(list(details)).drop('_id',axis=1)
        df['New_Subscription_Start']=pd.to_datetime(df.New_Subscription_Start,format="%Y-%m-%d", errors='coerce').dt.date
        df.sort_values(by='New_Subscription_Start', inplace=True)
        df2=df[['Name','Email','Usage','Country','Phone','Previous_Amount','Currency',\
            'Renewed_Amount','Date_joined','New_Subscription_Start','New_Subscription_End',\
                'Difference_Days','Plan_Name','Payment_mode']]
        return df2

def get_ammount_paid(email):
    l=get_enroll_data([email])
    # details=collection.find({'email':str(email)})
    # df=pd.DataFrame.from_records(list(details)).drop('_id',axis=1)
    # df['current_period_start']=pd.to_datetime(df.current_period_start,format="%Y-%m-%d", errors='coerce').dt.date
    # df.sort_values(by='current_period_start', inplace=True, ascending=False)
    return(float(l[0]['last_Amount_Paid_by_Customer']), l[0]['country'], l[0]['Join_Date'])

def get_sessions_date(from_date,to_Date):
    collection = db["sessions"]
    details=collection.find({})
    df=pd.DataFrame.from_records(list(details)).drop('_id',axis=1)

    df = df.loc[df["Date_of_Session"].between(str(from_date), str(to_Date))]

    df['Project_ID']=df['Project_ID'].astype(str)
    df['Date_of_Session']=pd.to_datetime(df.Date_of_Session,format="%Y-%m-%d", errors='coerce')
    df.sort_values(by='Date_of_Session', inplace=True)
    df.rename(columns = {'Email':'Customer_Email'}, inplace = True)
    if('duration_of_call' in df.columns):
        df2=df[['Name_of_Expert','Date_of_Session','Time_of_Session','duration_of_call','Domain_query','Customer_Email','Session_Completed','session_status']]
    else:
        df2=df[['Name_of_Expert','Date_of_Session','Time_of_Session','Domain_query','Customer_Email','Session_Completed','session_status']]
    #df2=df[['Name_of_Expert','Date_of_Session','Time_of_Session','Domain_query','Customer_Email','Session_Completed','session_status']]
    return df2

def get_renewals_date(from_date,to_Date):
    collection = db["renewals"]
    details=collection.find({})
    df=pd.DataFrame.from_records(list(details)).drop('_id',axis=1)
    df2 = df.loc[df["New_Subscription_Start"].between(str(from_date), str(to_Date))]
    if(df2.empty==True):
        return pd.DataFrame()
    else:
        df2['New_Subscription_Start']=pd.to_datetime(df2.New_Subscription_Start,format="%Y-%m-%d", errors='coerce').dt.date
        df2.sort_values(by='New_Subscription_Start', inplace=True)
        df2=df2[['Name','Email','Usage','Country','Phone','Previous_Amount','Currency',\
            'Renewed_Amount','Date_joined','New_Subscription_Start','New_Subscription_End',\
                'Difference_Days','Plan_Name','Payment_mode']]
        return df2

def get_retained_date(from_date,to_date):
    collection = db["onboard_refund"]
    c=list(collection.find({'$or':[{"Status":"Retained"},{"Status":"Retained with Partial Refund","Amount_Refunded":{'$ne':None}}]}))
    df=pd.DataFrame.from_records(c).drop('_id',axis=1)
    df = df.loc[df["Date_Requested"].between(str(from_date), str(to_date))]
    if(df.empty==True):
        return pd.DataFrame()
    else:
        details=get_refund_email(list(df['Email']))
        return details

def get_refund_date(from_date,to_date):
    collection = db["onboard_refund"]
    c=list(collection.find({"Status": {"$in":["Refunded","Partial refund to be processed","Refund in Progress","Retained with Partial Refund","Complete Refund to be processed"]}}))
    df=pd.DataFrame.from_records(c).drop('_id',axis=1)
    df = df.loc[df["Date_Requested"].between(str(from_date), str(to_date))]
    if(df.empty==True):
        return pd.DataFrame()
    else:
        
        details=get_refund_email(list(df['Email']))
        details['Status']=pd.Categorical(details['Status'],["Complete Refund to be processed","Partial refund to be processed","Refund in Progress","Retained with Partial Refund","Refunded"])
        details.sort_values(['Status','Date_Requested'], axis = 0, ascending = True, inplace = True, ignore_index=True, na_position ='last')
        
        return(details)


def get_refund_data(email):
    collection=db['onboard_refund']
    r=collection.find_one({'Email':email})
    return r


def get_refund_email(emails: list):
    if(type(emails)!=list):
        emails=[emails]

    collection = db["onboard_refund"]

    refund_data=collection.find({"Email":{"$in":emails}})
    df_main=pd.DataFrame.from_records(list(refund_data)).drop('_id',axis=1)
    df_main.rename(columns = {'Email':'_id', 'Amount':"Amount_to_Refund"}, inplace = True)
 
    df_enroll=pd.DataFrame.from_records(get_enroll_data(emails))

    df_sessions=pd.DataFrame.from_records(get_session_counts(emails))
  
    df_engage=pd.DataFrame.from_records(get_engage_stats(emails))
 
    if df_enroll.empty:
        df_enroll=pd.DataFrame({"_id":list(df_main['_id']),"last_Start_Date":[pd.NA]*df_main.shape[0],
                                "last_Amount_Paid_by_Customer":[pd.NA]*df_main.shape[0], "Join_Date":[pd.NA]*df_main.shape[0],
                                "country":[pd.NA]*df_main.shape[0]})
    
    df_main=df_main.merge(df_enroll, right_on='_id', left_on='_id' ,how='left')
 
    if df_sessions.empty:
        df_sessions=pd.DataFrame({"_id":list(df_main['_id']),"total_sessions":[pd.NA]*df_main.shape[0]})
    
    df_main=df_main.merge(df_sessions, right_on='_id', left_on='_id' ,how='left')
   
    if df_engage.empty:
        df_engage=pd.DataFrame({"_id":list(df_main['_id']),"totalCount":[pd.NA]*df_main.shape[0],
                                "Distinct_Projects_Count":[pd.NA]*df_main.shape[0], "total_lab":[pd.NA]*df_main.shape[0],
                                "total_watch":[pd.NA]*df_main.shape[0], "totalSum":[pd.NA]*df_main.shape[0]})
    
    df_main=df_main.merge(df_engage, right_on='_id', left_on='_id' ,how='left')
    
    df_main=df_main.drop_duplicates(ignore_index=True)
    df_main['Date_Requested']=pd.to_datetime(df_main.Date_Requested,format="%Y-%m-%d", errors='coerce').dt.date
    df_main.sort_values(by='Date_Requested', inplace=True, ascending=False, ignore_index=True)
    
    return(df_main[['_id','Status','last_Amount_Paid_by_Customer','Amount_to_Refund', 'Amount_Refunded',
                    'Join_Date','Date_Requested','total_sessions','Distinct_Projects_Count','total_lab',
                    'total_watch','totalSum','Currency','country','Note','Remarks Post Calling','Last_Conversation_Grade_Notes']])


def insert_refund_data(data):
    collection = db["onboard_refund"]
    collection.update_one({"Email":data['Email']},{"$set":data},upsert=True)
    return
    # r=collection.find_one({'Email':data['Email']})
    # if(r==None):
    #     collection.insert_one(data)
    #     return
    # else:
    #     collection.delete_many({'Email':data['Email']})
    #     collection.insert_one(data)
    #     collection.up
    #     return

def insert_renewal_data(data):
    collection = db["renewals"]
    collection.insert_one(data)
    return

def insert_expert(expert):
    db2 = client["Projects"]
    collection = db2["Experts"]
    collection.insert_one(expert)
    return

def fetch_experts(ex_email=None, ex_name=None):
    db2 = client["Projects"]
    collection = db2["Experts"]
    if(ex_name==None):
        r = collection.find({})
    elif(ex_name!=None):
        r = collection.find({'name':str(ex_name)})
    name=list()
    email=list()
    for i in r:
        name.append(i['name'])
        email.append(i['email'])

    return (name,email)

def send_mail(receiver,subject,body):
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    
    # start TLS for security
    s.starttls()
    
    # Authentication
    s.login("kedar@dezyre.com", creds.PW)
    
    # message to be sent
    message = "Subject:{}\n\n{}".format(subject,body)
    
    # sending the mail
    s.sendmail("kedar@dezyre.com", receiver, message)
    
    # terminating the session
    s.quit()