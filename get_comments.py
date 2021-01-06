import tweepy
import json
from time import sleep
from re import search
from itertools import cycle
from random import shuffle
from datetime import datetime, timedelta
import re
from collections import Counter
import sys
from collections import defaultdict

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
# screen_name = "pestermutant"
# screen_name = "mergecook"
screen_name = "aikoharunoo"
# screen_name = "officialchidori"
consumer_key,consumer_secret,access_token,access_token_secret = keys_and_tokens[screen_name]["consumer_key"],keys_and_tokens[screen_name]["consumer_secret"],keys_and_tokens[screen_name]["access_token"],keys_and_tokens[screen_name]["access_token_secret"]
api = oauth_login(consumer_key,consumer_secret,access_token,access_token_secret)

with open("tweet_ids.txt",'r') as f:
    ids = f.read().split('\n')


replies=[]
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

# Use this to get comments from a specific user's tweets https://stellamindemography.wordpress.com/2018/05/04/mining-data-from-twitter-and-replies-to-tweets-with-tweepy/
username = "torpedoAIO"
with open("comments2.txt","a+") as f:
    for full_tweets in tweepy.Cursor(api.user_timeline,screen_name=username,timeout=999999).items(20):
        for tweet in tweepy.Cursor(api.search,q=f'to:{username}', result_type='recent',timeout=999999).items(1000):
            if hasattr(tweet, 'in_reply_to_status_id_str'):
                if (tweet.in_reply_to_status_id_str==full_tweets.id_str):
                    # replies.append(tweet.text)
                    comment = str(tweet.text).strip(f"@{username} ").replace('\n','').lower()
                    # print(f"reply of tweet: {comment}")
                    if (len(comment) > 15) and (not any(keyword in comment for keyword in ["https","@","wrath","torpedo"])):
                        f.write(comment+'\n')

        # print("Tweet :",full_tweets.text.translate(non_bmp_map))
        # for elements in replies:
        #     print("Replies :",elements)
        # replies.clear()

# Use this if I have a list of a bunch of status ids https://stackoverflow.com/questions/52307443/how-to-get-the-replies-for-a-given-tweet-with-tweepy-and-python
# for tweet_id in ids:
#     tweet_id = int(tweet_id)
#     with open("comments.txt","a") as f:
#         count = 0
#         status = api.get_status(tweet_id,tweet_mode="extended")
#         try:
#             replies = tweepy.Cursor(api.search, q=f'to:{status.user.screen_name}',since_id=tweet_id, tweet_mode='extended').items()
#             while True:
#                 try:
#                     reply = replies.next()
#                     if not hasattr(reply, 'in_reply_to_status_id_str'):
#                         continue
#                     if reply.in_reply_to_status_id == tweet_id:
#                        comment = str(reply.full_text).replace('\n','').strip(f"@{status.user.screen_name} ")
#                        # print(f"reply of tweet: {comment}")
#                        if ("@" not in comment) and (len(comment) > 12):
#                            f.write(comment+'\n')
#                            count += 1
#                            if count == 99:
#                                break
#                 except tweepy.RateLimitError as e:
#                     print("Twitter api rate limit reached".format(e))
#                     time.sleep(60)
#                     continue
#                 except tweepy.TweepError as e:
#                     print("Tweepy error occured:{}".format(e))
#                     continue
#                 except StopIteration:
#                     print("Stopped")
#                     continue
#                 except Exception as e:
#                     print("Failed while fetching replies {}".format(e))
#                     continue
#         except Exception as e:
#             print(e)
#             continue
