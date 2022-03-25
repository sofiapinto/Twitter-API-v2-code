#-------------------------
#-----PACKAGE IMPORTS-----
#-------------------------
#All the necessary packages to retrieve data from twitter API GET /2/users endpoint
import requests
import json
import time
import pandas as pd
import math

#-------------------
#-----FUNCTIONS-----
#-------------------

#Function to create endpoint URL
def create_url(user_IDs, fields):
    return "https://api.twitter.com/2/users?ids={}&user.fields={}".format(user_IDs, fields)

#Function to create headers using the bearer token:
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

#When there is an error I make my program sleep between 5 and 60 seconds before trying again:
def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        rn = random.randint(5,60)
        time.sleep(rn)
        return connect_to_endpoint(url, headers)
    return response.json()

#Function to save data in a json file:
def save_data(date, data, file_number):
    with open('./data/users_info_'+date+'_file'+str(file_number)+'.json','w', encoding='utf8') as tf:
        json.dump(data, tf, indent = 4, ensure_ascii = False)

#----------------------------------------------------
#-----SETTING UP VARIABLES BEFORE RETRIVING DATA-----
#----------------------------------------------------

#Date of data retrieval:
date = '2022_March_25'

#Users information:
user_info = pd.read_pickle('author_IDs.pkl')
user_info['author_id'] = user_info['author_id']+','

#Twitter API credentials. You just need to replace the XXX by your bearer token.
bearer_token = "XXX"

#Headers:
headers = create_headers(bearer_token)

#Setting up user fields we want to have access to:
user_fields = 'id,username,name,created_at,description,location,public_metrics,url,verified'

#-------------------------
#-----RETRIEVING DATA-----
#-------------------------
for i in range(math.ceil(len(user_info)/100)):
    if i != math.ceil(len(user_info)):
        user_IDs = user_info['author_id'][i*100:(i+1)*100].sum()[:-1]
    else:
        user_IDs = user_info['author_id'][i*100:].sum()[:-1]
    url = create_url(user_IDs, user_fields)
    
    json_response = connect_to_endpoint(url, headers)

    save_data(date, json_response, i)
    
    #sleep for 3.2 seconds not to surpass the rate limit
    time.sleep(3.2)