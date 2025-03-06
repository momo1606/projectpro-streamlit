from deta import Deta
from dotenv import load_dotenv
import os
#credentials for deta
!
DETA_KEY=''


#load the enviornment variables
# load_dotenv('.env')
# DETA_KEY=os.getenv('DETA_KEY')
# print(DETA_KEY)


# #initialize with project key
deta=Deta(DETA_KEY)

#create/connect to database
db=deta.Base('users_db')

#insert user
def insert_user(username,name,password):
    return db.put({'key':username,'name':name,'password':password})

insert_user('abhay','abhay kumar','abc123')

#fetch all users

def fetch_users():
    res=db.fetch()
    return res.items
