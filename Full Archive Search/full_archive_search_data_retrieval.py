#-------------------------
#-----PACKAGE IMPORTS-----
#-------------------------
#All the necessary packages to retrieve data from twitter API GET /2/tweets/search/all endpoint.
import requests
import os
import json
import time
import random

#---------------------
#-----CREDENTIALS-----
#---------------------
#Twitter API credentials. You just need to replace the XXX by your bearer token
bearer_token = "XXX"

#------------------------------------------
#-----FULL ARCHIVE SEARCH ENDPOINT URL-----
#------------------------------------------
search_url = "https://api.twitter.com/2/tweets/search/all"

#-------------------------------------------
#-----RULES/QUERIES FOR DATA EXTRACTION-----
#-------------------------------------------
#This json file contains the rule(s) for the data extraction.
with open('rules.json', 'r') as f:
    queries = json.load(f)

#-------------------
#-----FUNCTIONS-----
#-------------------
#Function to create headers using the bearer token:
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

#When there is an error I make my program sleep between 5 and 60 seconds before trying again:
def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", url, headers=headers, params=params)
    if response.status_code != 200:
        rn = random.randint(5,60)
        time.sleep(rn)
        return connect_to_endpoint(url, headers, params)
    return response.json()

#Transforming and saving data
def transform_JSON_response(json, data, users, tweets, places, errors):
    data = data + json['data']
    users = users + json['includes']['users']
    
    if 'tweets' in json['includes'].keys():
        tweets = tweets + json['includes']['tweets']
    
    if 'places' in json['includes'].keys():
        places = places + json['includes']['places']
    
    if 'errors' in json.keys():
        errors = errors + json['errors']
        
    return data, users, tweets, places, errors
def save_data(data, users, tweets, places, errors, query, file):
    with open('./data/data_query'+str(query)+'_file'+str(file)+'.json','w', encoding='utf8') as tf:
        json.dump(data, tf, indent = 4, ensure_ascii = False)

    with open('./data/users_query'+str(query)+'_file'+str(file)+'.json','w', encoding='utf8') as tf:
        json.dump(users, tf, indent = 4, ensure_ascii = False)
    
    with open('./data/tweets_query'+str(query)+'_file'+str(file)+'.json','w', encoding='utf8') as tf:
        json.dump(tweets, tf, indent = 4, ensure_ascii = False)

    with open('./data/places_query'+str(query)+'_file'+str(file)+'.json','w', encoding='utf8') as tf:
        json.dump(places, tf, indent = 4, ensure_ascii = False)

    with open('./data/errors_query'+str(query)+'_file'+str(file)+'.json','w', encoding='utf8') as tf:
        json.dump(errors, tf, indent = 4, ensure_ascii = False)

#Function to reset lists to empty:
def reset_lists():
    return [], [], [], [], []


#--------------------------------------
#-----RETRIEVING DATA FROM THE API-----
#--------------------------------------

#Headers:
headers = create_headers(bearer_token)

#Dates and times to cover (in UTC time):
#One just needs to set this according to the time range needed.
datetime_start = "2020-01-01T00:00:00Z"
datetime_end = "2020-01-02T23:59:59Z"

#Retrieving and saving tweets:
for i in range(len(queries['rules'])):
    #reset lists to empty
    list_data, list_includes_users, list_includes_tweets, list_includes_places, list_errors = reset_lists()

    #set page and file to 1
    page = 1
    file = 1

    #define query parameters depending on query and start and end datetimes
    query_params = {'query': queries['rules'][i]['value'],
        'tweet.fields': 'id,text,author_id,context_annotations,conversation_id,created_at,entities,geo,in_reply_to_user_id,lang,public_metrics,referenced_tweets,reply_settings,source',
        'user.fields':'id,name,username,created_at,description,entities,location,public_metrics,url,verified',
        'place.fields':'full_name,id,contained_within,country,country_code,geo,name,place_type',
        'expansions':'author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id',
        'start_time':datetime_start,
        'end_time':datetime_end,
        'max_results':100
       }

    #getting first page of tweets
    json_response = connect_to_endpoint(search_url, headers, query_params)

    #sleep for 3.2 seconds not to surpass the rate limit
    time.sleep(3.2)

    if 'data' in json_response:
        #updating lists with new data
        list_data, list_includes_users, list_includes_tweets, list_includes_places, list_errors = transform_JSON_response(json_response, list_data, list_includes_users, list_includes_tweets, list_includes_places, list_errors)


    #if there are more tweets then the meta field will have a next token key-pair
    while 'next_token' in json_response['meta']:
        #updating the query parameters to specify the page, using the next token
        query_params['next_token'] = json_response['meta']['next_token']

        #getting next page of tweets
        json_response = connect_to_endpoint(search_url, headers, query_params)

        #sleep for 3.2 seconds not to surpass the rate limit
        time.sleep(3.2)


        if 'data' in json_response:
            #updating lists with new data
            list_data, list_includes_users, list_includes_tweets, list_includes_places, list_errors = transform_JSON_response(json_response, list_data, list_includes_users, list_includes_tweets, list_includes_places, list_errors)

        #update page number
        page = page + 1


        #if we get to the 25th page, we store data and reset the lists to empty
        #so that each one of the json files is not very big
        if page % 25 == 0:
            save_data(list_data, list_includes_users, list_includes_tweets, list_includes_places, list_errors, i, file)
            list_data, list_includes_users, list_includes_tweets, list_includes_places, list_errors = reset_lists()
            file = file + 1
    if len(list_data)>0 or len(list_includes_tweets)>0:
        save_data(list_data, list_includes_users, list_includes_tweets, list_includes_places, list_errors, i, file)