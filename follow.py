import tweepy
import json
from time import sleep
from re import search
from itertools import cycle
from random import shuffle
from datetime import datetime, timedelta
from sys import argv

def oauth_login(consumer_key,consumer_secret,access_token,access_token_secret):
    # Switch to application authentication - application-only authentication allows for 450 queries every 15 minutes
    # auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    # api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Setting up new api wrapper, using authentication only
    # User-authentication allows for 180 queries per access token every 15 minutes
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret) #Pass our consumer key and consumer secret to Tweepy's user authentication handler
    auth.set_access_token(access_token, access_token_secret) #Pass our access token and access secret to Tweepy's user authentication handler
    api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Creating a twitter API wrapper using tweepy
    return api

class TwitterFollowBot(object):
    """Twitter bot for following users"""
    def __init__(self, screen_name):
        with open('accounts_to_follow.json') as f:
            self.accounts_to_follow = json.load(f)["accounts_to_follow"]
        with open('keys_and_tokens.json') as f:
          self.keys_and_tokens = json.load(f)
        consumer_key,consumer_secret,access_token,access_token_secret = self.keys_and_tokens[screen_name]["consumer_key"],self.keys_and_tokens[screen_name]["consumer_secret"],self.keys_and_tokens[screen_name]["access_token"],self.keys_and_tokens[screen_name]["access_token_secret"]
        self.api = oauth_login(consumer_key,consumer_secret,access_token,access_token_secret)
        self.screen_name = screen_name
        # self.followers = self.api.followers_ids(self.screen_name) # returns list of user ids
        self.following = self.api.friends_ids(self.screen_name)

    # Writes all accounts to file for future use. Function must be ran after get_accounts_from_file() is called.
    def write_to_file(self):
        accounts_to_follow_dict = {"accounts_to_follow":list(set(self.accounts_to_follow)),"total_accounts":len(list(set(self.accounts_to_follow)))}
        with open("accounts_to_follow.json", 'w') as outfile:
            json.dump(accounts_to_follow_dict, outfile, sort_keys=True, indent=2)

    # Adds all accounts that were followed manually to pre-existing list of accounts I am currently following.
    def add_accounts_to_file(self):
        print("Checking for new users you followed...")
        new_users_followed_count = 0
        # main_screen_name = "aikoharunoo"
        # consumer_key,consumer_secret,access_token,access_token_secret = self.keys_and_tokens[main_screen_name]["consumer_key"],self.keys_and_tokens[main_screen_name]["consumer_secret"],self.keys_and_tokens[main_screen_name]["access_token"],self.keys_and_tokens[main_screen_name]["access_token_secret"]
        consumer_key,consumer_secret,access_token,access_token_secret = self.keys_and_tokens[self.screen_name]["consumer_key"],self.keys_and_tokens[self.screen_name]["consumer_secret"],self.keys_and_tokens[self.screen_name]["access_token"],self.keys_and_tokens[self.screen_name]["access_token_secret"]
        temp_api = oauth_login(consumer_key,consumer_secret,access_token,access_token_secret)
        following = temp_api.friends_ids(self.screen_name)
        for account in following:
            account_screen_name = temp_api.get_user(account).screen_name.lower() # Check rate limits with: temp_api.rate_limit_status()["resources"]["users"]["/users/:id"] you get 900 per 15 mins
            if (account_screen_name not in set(self.accounts_to_follow)):
                self.accounts_to_follow.append(account_screen_name)
                new_users_followed_count += 1
        self.write_to_file()
        print(f"✅ [{new_users_followed_count}] new users have been added! ")

    # Follows all accounts stored within accounts_to_follow.json
    def follow_accounts_from_file(self, *arg):
        # Follows each account mentioned in "accounts_to_follow" file
        print(f'**************** [{self.screen_name.upper()}] starting to follow users ****************')
        total_followed = 0
        for account in self.accounts_to_follow:
            try:
                # Checks if the account is already being followed
                user_id = self.api.get_user(account).id
                if user_id in set(self.following):
                    # print('---- [Already following ' + account + '] ----')
                    continue
                # Proceeds to follow users in account list
                self.api.create_friendship(account)
                print(f'Followed [{account}]')
                total_followed += 1
                sleep(10)
                # Takes a 2 minute break once it follows 10 users
                if total_followed % 10 == 0:
                    print(f'---- [ {str(total_followed)} users followed so far.] ----')
                    sleep(120)
                # Takes a 10 minute break once it follows 10 users
                if total_followed == 50:
                    print(f'---- [ {str(total_followed)} users followed so far.] ----')
                    sleep(600)
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                print(f'---- Error: {str(e)} for user: [{account}] ----\n')
                break
                sleep(600)
                continue
        print(f"**************** [{str(total_followed)}] users followed ****************\n")



if __name__ == '__main__':
    # Run this to automatically run accounts one after another
    with open('keys_and_tokens.json') as f:
        keys_and_tokens = json.load(f)

    # Run this to have ALL accounts follow accounts in file
    for screen_name in keys_and_tokens:
        bot = TwitterFollowBot(screen_name)
        bot.follow_accounts_from_file()

    # Run this to add all accounts that ONE user is following
    # bot = TwitterFollowBot("pestermutant")
    # bot.add_accounts_to_file()
