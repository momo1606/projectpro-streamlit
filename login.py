from operator import index
from textwrap import indent
import streamlit as st
import streamlit_authenticator as stauth
from app import *
import database as db
import io
import rev_expert
import utils
from utils import check_email,insert_email, insert_renewal_data,insert_session,insert_refund_data


#fetching users from database
users=db.fetch_users()
usernames=[user['key'] for user in users]
names=[user['name'] for user in users]
hashed_passwords=[user['password'] for user in users ]

authenticator = stauth.Authenticate(names,usernames,hashed_passwords,
    'some_cookie_name','some_signature_key',cookie_expiry_days=30)
name, authentication_status, username = authenticator.login('Login','main')

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

#Authentication
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.write('Welcome *%s*' % (name))
    st.image('logo_white.png', width=400)

    if username in['ankani','kedar','hassan']:

        #Application
        query = st.sidebar.selectbox('Select query', ["1:1 session",'See Customer History','Add new expert','View Sessions by Date'])
        if query=='1:1 session':
            c=one_to_one_data()
            #submit button
            if st.button('Submit', key='1:1 session'):
                if check_email({"_id": c['Email']}):

                    #inserting session into database
                    insert_session(c)
                    st.success('Data Uploaded !!')
                else:
                    st.write('Email id not in database.')
                    # insert_email({"_id": c['Email']})

                    # insert_session(c)
                    # st.success('Data Uploaded')

        elif query=='View Sessions by Date':
            st.title("View Sessions by Date")
            col1, col2 = st.columns(2)
            with col1:
                from_date=st.date_input("Enter from date")
            with col2:
                to_date=st.date_input('Enter to date')
            if st.button('Submit',key='ASD'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    details=utils.get_sessions_date(from_date,to_date)
                if details.empty:
                    st.write('No history of sessions for this date range')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Sessions_date.csv'))
        
        #see customer history
        elif query=='See Customer History':
            email=st.selectbox('Enter Email address',set(utils.fetch_emails()))
            if st.button('Submit', key='customer history'):
                details=utils.get_customer_details(email)
                if details.empty:
                    st.write('No history of sessions for this customer')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customer_sessions.csv'))
                    #details

        #add new expert
        elif query=='Add new expert':
            data={}
            ex_name=st.text_input('Name of expert')
            data['name']=ex_name
            email=st.text_input('Email of expert')
            data['email']=email
            if st.button('Add Expert',key='new expert'):
                utils.insert_expert(data)
                st.success('Expert Added')


    elif username in['shwetha','kedar']:
        query = st.sidebar.selectbox('Select query', ["Refund Data Form",'Renewal Data Form','View Renewals by Customer','View Renewals by Date','View Refund by Email ID','View Refunds by Date'])
        if query=='Refund Data Form':
            data = refund_data()
            if st.button('Submit',key='refund request'):
                
                if((data['Status'] in ['Refund in Progress','Partial refund to be processed','Complete Refund to be processed','Retained with Partial Refund']) and (data['Mode']=='Stripe') and (data['Conversation_Grade']=='Final response')):
                    mail_id="omair@projectpro.io"
                    subject="Refund and Subscription Termination - {}".format(data['Email'])
                    body="Hi Omair,\n After multiple conversations with the customer-{}, we have approved the Refund Amount of {} for the payment mode: \'Stripe\' on {}.\n Kindly end the subscription and process the refund. Below are the details for the same.\n".format(data['Email'],data['Amount'],datetime.datetime.now().strftime('%d-%m-%Y'))+json.dumps(data, indent=4)+"\nThank you\nShwetha"
                    try:
                        utils.send_mail(mail_id, subject, body)
                        if(data['Status']!="Retained with Partial Refund"):
                            data['Status']="Refunded"
                        data["Amount_Refunded"]=data['Amount']
                        st.success(f"Email sent to {mail_id}")
                    except Exception as e:
                        st.error(str(e))

                elif((data['Status'] in ['Refund in Progress','Partial refund to be processed','Complete Refund to be processed','Retained with Partial Refund']) and (data['Mode']!='Stripe') and (data['Conversation_Grade']=='Final response')):
                    mail_id="divya@projectpro.io"
                    subject="Process Refund - {}".format(data['Email'])
                    data_subset={k: data[k] for k in ('Email', 'Status','Date_Requested','Mode')}
                    data_subset['Amount_to_Refund']=data['Amount']
                    data_subset['Amount_paid_by_Customer']=utils.get_ammount_paid(data['Email'])[0]
                    body="Hi Divya,\n Kindly process refund for the customer - {}. Below are the details for the same.\n For more metrics about the customer's engagement, please check the streamlit dashboard.\n".format(data['Email'])+json.dumps(data_subset, indent=4)+"\nThank you\nShwetha"
                    try:
                        utils.send_mail(mail_id, subject, body)
                        st.success(f"Email sent to {mail_id}")
                    except Exception as e:
                        st.error(str(e))
                insert_refund_data(data)
                st.success('Data Uploaded')


        elif query=='Renewal Data Form':
            data=renewal_data()
            if st.button('Submit', key='renewal form'):
                insert_renewal_data(data)
                st.success('Data Uploaded')
        
        elif query=='View Renewals by Customer':
            
            st.title("View Renewals by Customer")
            email=st.selectbox('Enter Customer Email',set(utils.fetch_emails()))
            if st.button('Submit',key='VRC'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    details=utils.get_renewals_customer(email)
                if details.empty:
                    st.write('No history of renewals for this customer')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customer_renewals.csv'))
                    #details

        elif query=='View Renewals by Date':
            st.title("View Renewals by Date")
            col1, col2 = st.columns(2)
            with col1:
                from_date=st.date_input("Enter from date")
            with col2:
                to_date=st.date_input('Enter to date')
            if st.button('Submit',key='VCD'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    details=utils.get_renewals_date(from_date,to_date)
                if details.empty:
                    st.write('No history of renewals for this date range')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customers_renewals.csv'))
        
        elif query=='View Refund by Email ID':
            st.title("View Refund history by Email ID")
            email=st.selectbox('Enter Customer Email',set(utils.fetch_refund_emails()))
            if st.button('Submit',key='SRC'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    details=utils.get_refund_email(email)
                if details.empty:
                    st.write('No history of refund for this customer')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customer_refund.csv'))
                    #details
        
        elif query=='View Refunds by Date':
            st.title("View Refunds history by Date")
            col1, col2 = st.columns(2)
            with col1:
                from_date=st.date_input("Enter from date")
            with col2:
                to_date=st.date_input('Enter to date')
            if st.button('Submit',key='SCD'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    details=utils.get_refund_date(from_date,to_date)
                if details.empty:
                    st.write('No history of refunds for this date range')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customers_refunds.csv'))




    elif username in ['divya']:
        query = st.sidebar.selectbox('Select query', ["View Renewals by Date",'View Refunds by Date',\
            'View Refund by Email ID','Fill Refund Details','View Expert sessions history','Expert Revenue Share',\
                'View Retained Customers by Date', 'See Customer 1:1 Session History'])

        if query=='View Renewals by Date':
            st.title("View Renewals by Date")
            col1, col2 = st.columns(2)
            with col1:
                from_date=st.date_input("Enter from date")
            with col2:
                to_date=st.date_input('Enter to date')
            if st.button('Submit',key='VRDD'):
                details=utils.get_renewals_date(from_date,to_date)
                if details.empty:
                    st.write('No history of renewals for this date range')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customers_renewals.csv'))

        elif query=='See Customer 1:1 Session History':
            email=st.selectbox('Enter Email address',set(utils.fetch_emails()))
            if st.button('Submit', key='Divya customer history'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    details=utils.get_customer_details(email)
                if details.empty:
                    st.write('No history of sessions for this customer')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customer_sessions.csv'))

        elif query=='View Retained Customers by Date':
            st.title("View Retained Customers by Date")
            col1, col2 = st.columns(2)
            with col1:
                from_date=st.date_input("Enter from date")
            with col2:
                to_date=st.date_input('Enter to date')
            if st.button('Submit',key='DRD'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    details=utils.get_retained_date(from_date,to_date)
                if details.empty:
                    st.write('No history of retains for this date range')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customers_retained.csv'))
        
        elif query=="Expert Revenue Share":

            st.title("Expert Revenue Share")
            col1, col2 = st.columns(2)
            with col1:
                from_date=st.date_input("Enter from date")
            with col2:
                to_date=st.date_input('Enter to date')
            if st.button('Submit',key='DRS'):

                buffer = io.BytesIO()

                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    df1,df2 = rev_expert.get_expert_revenue_share(from_date,to_date) 

                # Create a Pandas Excel writer using XlsxWriter as the engine.
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df1.to_excel(writer, sheet_name='Sheet1')
                    df2.to_excel(writer, sheet_name='Sheet2')

                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.save()

                    st.download_button(
                        label="Download Excel File",
                        data=buffer,
                        file_name="expert_revenue.xlsx",
                        mime="application/vnd.ms-excel"
                    )

        elif query=='Fill Refund Details':
            data=refund_process()
            if st.button('Submit',key='refund process'):
                mail_id="omair@projectpro.io"
                subject="Subscription Termination - {}".format(data['Email'])
                body="Hi Omair,\n After multiple conversations with the customer-{}, we have approved and processed the Refund Amount of {} on {}.\n Kindly end the subscription. Below are the details for the same.\n".format(data['Email'],data['Amount_Refunded'],datetime.datetime.now().strftime('%d-%m-%Y'))+json.dumps(data, indent=4)+"\nThank you\nDivya"
                try:
                    utils.send_mail(mail_id, subject, body)
                    if(data['Status']!="Retained with Partial Refund"):
                        data['Status']="Refunded"
                    st.success(f"Email sent to {mail_id}")
                except Exception as e:
                    st.error(str(e))

                insert_refund_data(data)
                st.success('Data Uploaded')

                mail_id="shwetha@projectpro.io"
                subject="Refund Processed - {}".format(data['Email'])
                body="Hi Shwetha,\n I have processed the refund for the customer - {} of Amount {}, on {} \n".format(data['Email'],data['Amount_Refunded'],datetime.datetime.now().strftime('%d-%m-%Y'))+"\nThank you\nDivya"
                try:
                    utils.send_mail(mail_id, subject, body)
                    st.success(f"Email sent to {mail_id}")
                except Exception as e:
                    st.error(str(e))

                
        elif query=='View Refund by Email ID':
            st.title("View Refund history by Email ID")
            email=st.selectbox('Enter Customer Email',set(utils.fetch_refund_emails()))
            if st.button('Submit',key='DRC'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    details=utils.get_refund_email(email)
                if details.empty:
                    st.write('No history of refund for this customer')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customer_refund.csv'))
                    #details
        
        elif query=='View Refunds by Date':
            st.title("View Refunds history by Date")
            col1, col2 = st.columns(2)
            with col1:
                from_date=st.date_input("Enter from date")
            with col2:
                to_date=st.date_input('Enter to date')
            if st.button('Submit',key='DCD'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    details=utils.get_refund_date(from_date,to_date)
                if details.empty:
                    st.write('No history of refunds for this date range')
                else:
                    st.dataframe(details)
                    csv=convert_df(details)
                    st.download_button(label="Download Data as CSV", data=csv, file_name=str('Customers_refunds.csv'))


        elif query=='View Expert sessions history':
            st.title("View Expert sessions history")
            expert_name=st.selectbox('Enter Expert Name',utils.fetch_experts()[0])
            expert_email=utils.fetch_experts(ex_name=expert_name)[1][0]
            #print(type(expert_email))
            st.write('Expert Email ID - '+expert_email)
            if st.button('Submit', key='VES'):
                with st.spinner("*%s* :hand_with_index_and_middle_fingers_crossed: ... (pun intended :sunglasses:)"%"Fetching Dezyre-d Data"):
                    ex_details=utils.get_expert_sessions(expert_email)
                if ex_details.empty:
                        st.write('No history of sessions for this Expert')
                else:
                    to_show=ex_details.copy()
                    to_show["Date_of_Session"]=to_show["Date_of_Session"].dt.date
                    st.dataframe(to_show.sort_values(by='Date_of_Session'))

                    current_month=ex_details[ex_details["Date_of_Session"].dt.month == datetime.datetime.now().month]
                    csv1=convert_df(current_month.sort_values(by='Date_of_Session'))

                    last_month=ex_details[ex_details["Date_of_Session"].dt.month == datetime.datetime.now().month-1]
                    csv2=convert_df(last_month.sort_values(by='Date_of_Session'))

                    csv3=convert_df(to_show.sort_values(by='Date_of_Session'))

                    col1,col2,col3 = st.columns(3)
                    with col1:
                        st.download_button(label="Download current month data as CSV", data=csv1, file_name=str(expert_name+'_this_month_sessions.csv'))

                    with col2:
                        st.download_button(label="Download last month data as CSV", data=csv2, file_name=str(expert_name+'_last_month_sessions.csv'))

                    with col3:
                        st.download_button(label="Download Complete data as CSV", data=csv3, file_name=str(expert_name+'_all_sessions.csv'))
                    #ex_details

#if usermame/password isn't correct
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')