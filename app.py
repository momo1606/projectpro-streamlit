import pandas as pd
import streamlit as st
import pandas as pd
import json
import datetime
import utils


#function for 1:1 session data
def one_to_one_data():

    st.title("1:1 session form")

    data=dict()

    #customer email
    cust_email = st.selectbox('Email address of customer',set(utils.fetch_emails()))
    st.write(cust_email)
    data['Email']=cust_email

    #domain of query
    query_domain=st.selectbox("Domain of Query:",("Big Data","Data Science","Career Guidance","Consulting","Technical Session"))
    st.write(query_domain)
    data['Domain_query']=query_domain

    #if existing query or not
    existing_query=st.radio("Existing Project Query:",("Yes","No"))
    st.write(existing_query)
    data['Existing_Query']=existing_query

    if existing_query=="Yes":
        #project name
        project_name=st.selectbox("Project Name:", utils.fetch_project_titles())
        data['Project_Name']=project_name
        id=int(utils.get_project_id(str(project_name)))
        data['Project_ID']=str(id)
        st.write("Project ID selected: "+str(id))

    elif existing_query=='No':
        data['Project_ID']='NA'
        data['Project_Name']='NA'


    #session topic
    topic = st.text_input("Session Topic")
    data['Session_Topic']=topic
    col1, col2 = st.columns(2)
    with col1:

        #session date
        session_date = st.date_input("Session Date")
        data['Date_of_Session']=str(session_date)
    with col2:

        #session time
        session_time = st.time_input("Time of session",datetime.time(1,10))
        st.write(session_time)
        data['Time_of_Session']=str(session_time)

    #name of expert
    name = st.selectbox('Name Of expert',utils.fetch_experts()[0])
    data['Name_of_Expert']=name

    #expert email
    exp_email=st.selectbox('Expert Email:',utils.fetch_experts()[1])
    data['Expert_Email']=exp_email

    #query resolved or not
    query_res = st.radio("Query Resolved:", ("Yes", "No"))
    data['Query_Resolved']=query_res

    #duration of call
    duration=st.selectbox('Duration of call',('30 minutes','1 hour','1.5 hours', '2 hour','greater then 2 hour'))
    data['duration_of_call']=duration

    #another session required
    another_session = st.radio("Need another session over same topic:", ("Yes", "No"))
    data['Need_Another_Session']=another_session

    #expert remarks
    remarks = st.text_area('Expert Remarks:')
    data['Expert_Remark']=remarks

    #customer feedback
    cust_feed = st.text_area("Customer feedback:")
    data['Customer_feedback']=cust_feed

    #session completed or not
    session_rs = st.selectbox("Session Completed:", ("Yes", "No"))
    data['Session_Completed']=session_rs

    if session_rs == "No":
        #reason for non-completion of session
        session_update = st.selectbox("Reason for non-completion of session:", ("Rescheduled", "Cancelled","Customer Noshow",
                                                                                "Expert Noshow","Technical Issue"))
        data['session_status']=session_update
        if session_update == "Cancelled":
            #reason for cancellation
            reason = st.text_area("Reason for cancellation:")
            data['Reason_for_Cancellation']=reason
            data['Rescheduled_Date'] = 'NA'
            data['Rescheduled_Time'] = 'NA'

        elif session_update == "Rescheduled":
            data['Reason_for_Cancellation'] = 'NA'
            col3, col4 = st.columns(2)
            with col3:
                #session rescedule date
                reschedule_date = st.date_input("Rescheduled Date")
                data['Rescheduled_Date']=str(reschedule_date)
            with col4:
                #session reschedule time
                reschedule_time = st.time_input("Rescheduled time",datetime.time(1,10))
                data['Rescheduled_Time']=str(reschedule_time)

        elif session_update=='Customer Noshow':
            data['Reason_for_Cancellation']='NA'
            data['Rescheduled_Date'] = 'NA'
            data['Rescheduled_Time'] = 'NA'

        elif session_update=='Expert Noshow':
            data['Reason_for_Cancellation']='NA'
            data['Rescheduled_Date'] = 'NA'
            data['Rescheduled_Time'] = 'NA'

        else:
            data['Reason_for_Cancellation']='NA'
            data['Rescheduled_Date'] = 'NA'
            data['Rescheduled_Time'] = 'NA'

    else:
        data['session_status']='NA'
        data['Reason_for_Cancellation']='NA'
        data['Rescheduled_Date']='NA'
        data['Rescheduled_Time']='NA'

    return data

#Customer renewal data
def renewal_data():
    
    st.title('Renewal Data Form')
    data=dict()

    email=st.selectbox('Email of Customer',set(utils.fetch_emails()))
    data['Email']=email

    name=st.text_input('Name of Customer')
    data['Name']=name

    usage=st.number_input('Usage Amount', value=0, format='%d')
    data['Usage']=usage

    country=st.selectbox('Customer Type',['Domestic', 'International'])
    data['Country']=country

    phone=st.number_input('Phone number', value=0, format='%d' , help='Enter country code without prefix \'00\'')
    data['Phone']=phone

    prev_amount=st.number_input('Previous Amount')
    data['Previous_Amount']=prev_amount

    currency=st.selectbox('Currency',utils.fetch_payment_currencies())
    data['Currency']=currency

    renew_amnt=st.number_input('Renewed Amount')
    data['Renewed_Amount']=renew_amnt

    discount=st.number_input('Discount Given', value=prev_amount-renew_amnt)
    data['Discount']=discount

    date_joined=st.date_input('Date Joined')
    data['Date_joined']=str(date_joined)

    new_start=st.date_input('New-Subscription Start Date')
    data['New_Subscription_Start']=str(new_start)

    new_end=st.date_input('New-Subscription End Date')
    data['New_Subscription_End']=str(new_end)

    diff=st.number_input('Difference in Days', value=0, format='%d')
    data['Difference_Days']=diff

    plan_name=st.text_input('Plan Name')
    data['Plan_Name']=plan_name

    # Plan_id=st.number_input('Plan ID', value=0, format='%d')
    # data['Plan_id']=Plan_id

    # proj_title=st.text_input('Project Title')
    # data['Project_title']=proj_title

    payment_mode=st.selectbox('Payment Mode',utils.fetch_payment_modes())
    data['Payment_mode']=payment_mode

    # ref=st.text_input('Referral Page')
    # data['Refferal_page']=ref

    # land_page=st.text_input('Landing Page')
    # data['Landing_page']=land_page

    # land_recipe=st.text_input('Landing Page for Recipe')
    # data['Landing_page_for_recipe']=land_recipe

    Auto_renewal=st.radio("Enrolled in Auto Renewal",['Yes', 'No'])
    if (Auto_renewal=='Yes'):
        data['Auto_renewal']='Y'
        data['Auto_renewal_stop_date']='NA'
    else:
        data['Auto_renewal']='N'
        Auto_renewal_stop_date=st.date_input('Auto Renewal Stop Date')
        data['Auto_renewal_stop_date']=str(Auto_renewal_stop_date)
    
    Notes=st.text_area("Notes")
    data['Notes']=Notes



    return data

#Customer refund data
def refund_data():    

    st.title('Refund Request Form')

   
    #Email
    email=st.selectbox('Email of customer',set(utils.fetch_emails()))

    r=utils.get_refund_data(email)
    y,z=None, None
    if(r == None):
        #data dictionary
        data={ 'Date_Enrolled': None,
            'Date_Requested': None,
            'validate_period': 0.0,
            'Email': email,
            'Reason': None,
            'Onboarding_Status': None,
            'Counselor_Name': None,
            'Conversation_Grade': None,
            'Status': None,
            'Process_Date_Updates': None,
            'Refunded_Date': None,
            'Amount': 0.0,
            'Amount_Refunded': None,
            'Mode': None,
            'Note': "",
            'Remarks Post Calling': "",
            'Currency': None,
            'residency_of_client': None,
            'Last_Conversation_Grade_Date':None,
            'Last_Conversation_Grade_Notes':""}
    else:
        data=r
        if(data['Date_Requested'] != None):
            y=datetime.datetime.strptime(data['Date_Requested'], "%Y-%m-%d").date()
        if(data['Last_Conversation_Grade_Date'] != None):
            z=datetime.datetime.strptime(data['Last_Conversation_Grade_Date'], "%Y-%m-%d").date()

    data['Email']=email
    last_amount_paid, origin_country, d_joined=utils.get_ammount_paid(email)
    st.write(f"Amount paid by the customer (from Country - {origin_country}) is {last_amount_paid}")

    if(type(data['Amount_Refunded'])==float and data['Amount_Refunded']==0.0):
        data['Amount_Refunded']=None
    if (data['Amount_Refunded']!=None):
        st.warning(f'{data["Status"]} - Amount {data["Amount_Refunded"]}, Please select another Customer')
        st.stop()
    #reason for refund
    reasons=['Dispute Case',
        'Dispute Issue',
        'Documentation issue',
        'Domain changed',
        'Health Issues',
        'Lab issue',
        'Medical Issue',
        'Misuse Case',
        'Needs to brush up knowledge first',
        'No reason',
        'No time to use it',
        None,
        'Price issue',
        'Project issue',
        'Renewal Refund',
        'Support issue',
        'Video issue',
        'implementation issue']
    reason=st.selectbox('Reason of refund',reasons, index=reasons.index(data['Reason']))
    data['Reason']=reason

    #date enrolled
    col1,col2=st.columns(2)
    with col1:
        date_enrolled=st.date_input('Date Enrolled', value=datetime.datetime.strptime(d_joined, "%Y-%m-%d").date())
        data['Date_Enrolled']=str(date_enrolled)

    with col2:
        date_requested=st.date_input('Date Requested', value=y)
        data['Date_Requested']=str(date_requested)
    
    
    #validation period
    calculated_val_period=date_requested-date_enrolled
    val_period=st.number_input('Validation Period', value=calculated_val_period.days)
    data['validate_period']=val_period

    #on boarding status
    onboard_statuses=['Yes','No',None]
    onboard_status=st.selectbox('Onoaboarding Status',('Yes','No',None), index=onboard_statuses.index(data['Onboarding_Status']))
    data['Onboarding_Status']=onboard_status

    #counselor name
    counselor_name=st.text_input('Counselor Name', value=data['Counselor_Name'])
    data['Counselor_Name']=counselor_name

    Last_Conversation_Grade_Date=st.date_input('Last Conversation Grade Date', value=z)
    data['Last_Conversation_Grade_Date']=str(Last_Conversation_Grade_Date)

    conGrades=[None,
        'Final response',
        'Third response',
        'First response given',
        'Fourth response',
        'Second response',
        'Fifth response']

    if(r != None):
        prevNotes=list(data['Last_Conversation_Grade_Notes'].split("|"))
        with st.expander("View Previous Conversations"):
            for i in prevNotes:
                st.write(i)
                st.write("*****")
            st.write("Additional Notes- \n *%s*" % str(data['Note']))
            st.write("Remarks Post Calling- \n *%s*" % str(data['Remarks Post Calling']))

    #conversation grade
    conv_grade=st.selectbox('Conversation Grade',conGrades, index=conGrades.index(data['Conversation_Grade']))
    data['Conversation_Grade']=conv_grade

    Last_Conversation_Grade_Notes=st.text_area("New Conversation Grade Notes",value=data['Last_Conversation_Grade_Notes'])
    temp=data['Last_Conversation_Grade_Notes']
    if(Last_Conversation_Grade_Notes!=""):
        data['Last_Conversation_Grade_Notes']=temp+' | '+Last_Conversation_Grade_Notes

    '''
    to use for Divya -
    Complete Refund to be processed
    Partial refund to be processed
    Refund in Progress
    Retained with Partial Refund
    '''
    statuses=['Complete Refund to be processed',
 'Dispute Case',
 'Need to discuss internally',
 None,
 'Not Eligible',
 'Partial refund to be processed',
 'Refund in Progress',
 'Retained',
 'Retained with Partial Refund',
 'Retention in Progress',
 "Waiting for the cx's response"]
    #status
    status=st.selectbox('Status',statuses,index=statuses.index(data["Status"]))
    data['Status']=status

    #process date updates
    # process_date_updates=st.text_input('Process Date Updates')
    # data['Process_Date_Updates']=process_date_updates

    #refund date
    # refund_date=st.date_input('Refunded Date')
    #data['Refunded_Date']=None

    #amount
    amount=st.number_input('Amount to be refunded', value=data["Amount"])
    data['Amount']=amount

    currency_list=utils.fetch_payment_currencies()
    currency=st.selectbox('Currency',currency_list, index=currency_list.index(data["Currency"]))
    data['Currency']=currency

    residency_list=['Domestic', 'International',None]
    residency=st.selectbox('Residency of Customer',residency_list,index=residency_list.index(data['residency_of_client']))
    data['residency_of_client']=residency

    #amount refunded
    # amt_refunded=st.number_input('Amount Refunded')
    #data['Amount_Refunded']=None

    #mode
    modes_list=['Affirm',
 'Eduvanz EMI',
 None,
 'Other',
 'Part payment EMI',
 'RazorPay',
 'Shopse EMI',
 'Stripe']
    mode=st.selectbox('Mode',modes_list,index=modes_list.index(data['Mode']), help="If mode is \'Stripe\' and Conversation Grade is \'Final response\' , Mail will be sent to Omair for Refund")
    data['Mode']=mode

    #customer time on platform
    # eng_time=st.number_input('Time spent by customer on platform')
    # data['enagagemnt_time']=eng_time

    #note
    note=st.text_area('Additional Note', value=data['Note'])
    temp2=data['Note']
    if(note!=""):
        data['Note']=temp2+" | "+note

    #remarks post calling
    remarks=st.text_area('Remarks Post Calling',value=data['Remarks Post Calling'])
    temp3=data['Remarks Post Calling']
    if(remarks!=""):
        data['Remarks Post Calling']=temp3+" | "+remarks
    

    return data

def refund_process():
    st.title('Refund Processing Form')
    
    l=utils.fetch_refund_process_emails()
    if not l:
        st.warning(f'No Domestic Customers for Refund with Final Response status')
        st.stop()

    email=st.selectbox('Email of customer',set(l))

    data=utils.get_refund_data(email)

    last_amount_paid, origin_country, d_joined=utils.get_ammount_paid(email)
    st.write(f"Amount paid by the customer (from Country - {origin_country}) is {last_amount_paid}")

    amount_refunded=st.number_input('Enter the Amount Refunded', value=data['Amount'])
    data['Amount_Refunded']=amount_refunded

    currency_list=utils.fetch_payment_currencies()
    currency=st.selectbox('Currency',currency_list, index=currency_list.index(data["Currency"]))
    data['Currency']=currency

    date_refunded=st.date_input("Date Refunded")
    data['Refunded_Date']=date_refunded

    notes=st.text_area("Additional Notes Post Refund")
    data['Note_refun']=notes

    return data


    
