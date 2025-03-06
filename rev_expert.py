import pandas as pd
import datetime
import pymongo


#get engage data from mongo
def get_engagement_mongo(fromdate, todate):
        ''''
        Function to Fetch engagement data from MongoDB
        The client is on mohammed's personal server
        
        Input:
        fromdate: data will be fetched from this date
        eg.
        fromd=datetime.datetime.strptime("2022-09-16", "%Y-%m-%d")
        todate: date will be fetched till this date

        Output:
        df: engagment_lab data fetched from mongo with given parameters    
        
        '''
        
        #connecting to mongo
        client = pymongo.MongoClient("")
        db = client["Customers"]
        collection = db["engage_lab_data"]

        #filtering data wrt dates
        cursor=collection.find({"date_created_timestamp":{"$gte": fromdate,"$lte":todate}})

        #fetching the data
        list_cur = list(cursor)

        #converting the data to dataframe
        df = pd.DataFrame(list_cur)   
        return df

#get engage data from mongo
def get_project_details():
        ''''
        Function to Fetch project tracker data from MongoDB
        The client is on mohammed's personal server
        
        Input:

        Output:
        df: project tracker data fetched from mongo with given parameters    
        
        '''
        
        #connecting to mongo
        client = pymongo.MongoClient("")
        db = client["Projects"]
        collection = db["ProjectDetails"]
        
        #filtering data wrt dates
        cursor=collection.find()
        
        #fetching the data
        list_cur = list(cursor)
        
        #converting the data to dataframe
        df = pd.DataFrame(list_cur)
   
        return df

def get_monthly_engagment(tod, fromd):
        """
        Function to get monthly engagment for all users

        Input:
        str_tod: date to which monthly engagement is required in str format  
        str_fromd: date from which monthly engagement is required in str format

        Output:
        monthly_user_projects: monthly user engagement dataframe
        """

        engage_lab=get_engagement_mongo(todate=tod, fromdate=fromd)

        engage=engage_lab[engage_lab['Category']=='Engagement']
        engage['project_id']=engage['project_id'].astype('int64')
        engage['year_month_created']=engage['date_created_timestamp'].dt.strftime('%Y-%m')

        monthly_user_projects=engage.groupby(['email','year_month_created','project_id','title','type'],as_index=False).agg(total_monthly_time_mins=('view_time','sum'))

        return monthly_user_projects        
                
def get_expert_usage(monthly_user_projects,required_experts=['Snehil', 'Sourabh', 'Rupak', 'Divya', 'Shraddha', 'Kedar','Shaurya', 'Akshay-Adarsh']):
        """
        function to get monthly usage for experts

        Input:
        monthly_user_projects: monthly usage data for all the customers acorss projects
        reuired_experts: experts for which the usage needs to be calculated. this has default value as of now might need to change as per the requirements

        Output:
        expert_pivot_df: expertwise monthly usage wrt each project 

        """
        
        #fetching project details
        projects=get_project_details()
        #renaming and getting required columns
        projects=projects.rename(columns={'_id':'project_id'})
        projects=projects[['project_id','Expert']]        

        #addding expert in monthly_usage data        
        expert_usage=monthly_user_projects.merge(projects,on='project_id',how='right')

        #selecting data fro required experts        
        requirerd_expert_usage_1=expert_usage[expert_usage.Expert.isin(required_experts)]   

        #grouping experts usage wrt year month and title
        requirerd_expert_usage=requirerd_expert_usage_1.groupby(['Expert','title','year_month_created'],as_index=False).agg({'total_monthly_time_mins':'sum'})

        #converting the data as per requirements
        expert_pivot=requirerd_expert_usage.pivot(index=['Expert','title'],columns='year_month_created',values='total_monthly_time_mins')
        expert_pivot_df=pd.DataFrame(expert_pivot.to_records())
        return expert_pivot_df



def get_expert_revenue_share(from_date,to_Date):
        #ask this to divya on streamlit and change the format in datetime object as per streamlit
        str_tod=str(to_Date) 
        str_fromd=str(from_date) 


        tod=datetime.datetime.strptime(str_tod, "%Y-%m-%d")
        fromd=datetime.datetime.strptime(str_fromd, "%Y-%m-%d")

        #showcase these two dataframes to divya

        monthly_engagement=get_monthly_engagment(tod, fromd) #name: Monthly engagement data from tod to fromd
        expert_engagement=get_expert_usage(monthly_user_projects=monthly_engagement) #name: expertwise engagement from tod to fromd

        return(monthly_engagement,expert_engagement)

