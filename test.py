import tweepy
import json
from time import sleep
from re import search
from itertools import cycle
from random import shuffle
from datetime import datetime, timedelta
from sys import argv
import re
from collections import Counter

def oauth_login(consumer_key,consumer_secret,access_token,access_token_secret):
    # Switch to application authentication - application-only authentication allows for 450 queries every 15 minutes
    # auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    # api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Setting up new api wrapper, using authentication only
    # User-authentication allows for 180 queries per access token every 15 minutes
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret) #Pass our consumer key and consumer secret to Tweepy's user authentication handler
    auth.set_access_token(access_token, access_token_secret) #Pass our access token and access secret to Tweepy's user authentication handler
    api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Creating a twitter API wrapper using tweepy
    return api

with open('keys_and_tokens.json') as f:
    keys_and_tokens = json.load(f)



# entities
# - {'hashtags': [], 'symbols': [], 'user_mentions': [], 'urls': [{'url': 'https://t.co/F9a4Q30uGN', 'expanded_url': 'https://twitter.com/rushaio/status/132704
# 5835977355266', 'display_url': 'twitter.com/rushaio/status…', 'indices': [42, 65]}]}

# user
# - {'id': 988628934538551296, 'id_str': '988628934538551296', 'name': 'Rush', 'screen_name': 'RushAIO', 'location': '', 'description': 'Where innovation meets automation. macOS & Windows.', 'url': 'https://t.co/INwY1obvmD', 'entities': {'url': {'urls': [{'url': 'https://t.co/INwY1obvmD', 'expanded_url': 'https://rushaio.co', 'display_url': 'rushaio.co', 'indices': [0, 23]}]}, 'description': {'urls': []}}, 'protected': False, 'followers_count': 39632, 'friends_count': 12, 'listed_count': 52, 'created_at': 'Tue Apr 24 04:01:20 +0000 2018', 'favourites_count': 757, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 1899, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://pbs.twimg.com/profile_images/1222316325747466240/9QDKukYg_normal.jpg', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/1222316325747466240/9QDKukYg_normal.jpg', 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/988628934538551296/1580258949', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': False, 'default_profile': True, 'default_profile_image': False, 'following': True, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none'}

# screen_name = "chazeichazy"
screen_name = "aikoharunoo"
# screen_name = "pestermutant"
# screen_name = "mergecook"
# screen_name = "officialchidori"
consumer_key,consumer_secret,access_token,access_token_secret = keys_and_tokens[screen_name]["consumer_key"],keys_and_tokens[screen_name]["consumer_secret"],keys_and_tokens[screen_name]["access_token"],keys_and_tokens[screen_name]["access_token_secret"]
temp_api = oauth_login(consumer_key,consumer_secret,access_token,access_token_secret)
# api = oauth_login(consumer_key,consumer_secret,access_token,access_token_secret)

# temp_status = temp_api.get_status(1339270315667550208,tweet_mode="extended")
# temp_status = temp_api.get_status(1339619003766087685)

print(temp_api.get_user("stockcopaio").id)

# for hashtag in temp_status.entities['hashtags']:
#     print(f"#{hashtag['text']} ")

# tweet_text = temp_status.full_text
# tweet_author = temp_api.get_status(temp_status.id).user.screen_name
# comment = f"@{tweet_author} "
# if len(temp_status.entities['hashtags']) == 0:
#     print('if')
#     # Sometimes tweets asks you to comment a specific thing down
#     specific_comment = re.findall(r'"([^"]*)"', tweet_text)
#     if specific_comment != []:
#         comment += specific_comment[0].replace('"', '').replace("'", '')
#     else: # Chooses a random comment to reply to the tweet
#         comment += random.choice(self.comments)
# else:
#     print('else')
#     # Adds each hashtag to the comment
#     for hashtag in temp_status.entities['hashtags']:
#         comment += f"#{hashtag['text']} "

# print(comment)

















# getting mentions https://www.youtube.com/watch?v=-4MvUXJutDI
# for i in temp_api.mentions_timeline(1):
#     print(i.created_at)



#
