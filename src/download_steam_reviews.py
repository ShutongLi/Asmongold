import requests
import datetime
import urllib
import json
import pandas as pd
import copy
import time
import random

URL = 'https://store.steampowered.com/appreviews/{appid}?{args}'
COLUMNS = ['review', 'timestamp_created', 'votes_up', 'votes_funny', 'weighted_vote_score', 'comment_count']

# clean the data
def clean_data(reviews, columns = COLUMNS):
    reviews = reviews[columns].copy()
    reviews['timestamp_created'] = reviews['timestamp_created'].apply(ts_to_date)
    return reviews

# just turns time stamp to formated datetime
def ts_to_date(timestamp, strfmt='%Y/%m/%d'):
    return datetime.datetime.fromtimestamp(timestamp).strftime(strfmt)

# the function that downloads reviews from steampowered as json
def get_reviews(URL=URL, appid=39210, review_filter = 'recent', is_json=1, cursor='*', num_per_page=100, stop_till='2021/05/01', 
                size_limit = 10000):
    # construct url argument from function arguments as dictionary
    # this is done for later easier cursor update
    arg_dict = {'json':is_json, 'cursor':cursor, 'num_per_page': num_per_page, 'filter': review_filter}
    
    #start going through pages to download reviews
    local_data = pd.DataFrame()
    latest_date = ts_to_date(time.time())
    earliest_date = ts_to_date(time.time())
    while earliest_date >=  stop_till:
        # urlencodes json into url arguments
        args = urllib.parse.urlencode(arg_dict)
        # constrcut the url that points towards the review page with the parameters given
        url = URL.format(appid=appid, args=args)
        print(f'visiting {url}')
        # download the json
        review_page = json.loads(requests.get(url).text)
        reviews, cursor = pd.DataFrame(review_page['reviews']), review_page['cursor']
        try:
            reviews = clean_data(reviews)
        except:
            reviews = pd.DataFrame()
        # update arg_dict
        arg_dict['cursor'] = cursor
        # update current_date for loop
        earliest_date = reviews['timestamp_created'].min()
        # add reviews to local_data
        local_data = local_data.append(reviews)
        # if the local_data is too large
        if local_data.shape[0] > size_limit:
            # save it to csv file 
            file_name = f'{latest_date}_to_{earliest_date}.csv'.replace('/','_')
            local_data.to_csv(f'./data/steam/{file_name}', index=False)
            latest_date = earliest_date
        # RIP ethical scraping
        time.sleep(random.randint(10, 20))
    # save rest of the file
    file_name = f'{latest_date}_to_{earliest_date}.csv'.replace('/','_')
    local_data.to_csv(f'./data/steam/{file_name}', index=False)

