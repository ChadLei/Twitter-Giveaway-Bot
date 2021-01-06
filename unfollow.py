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

class TwitterUnfollowBot(object):
    """Twitter bot for unfollowing users"""
    def __init__(self, screen_name):
        with open('accounts_to_follow.json') as f:
            self.accounts_to_follow = json.load(f)["accounts_to_follow"]
        with open('keys_and_tokens.json') as f:
          self.keys_and_tokens = json.load(f)
        consumer_key,consumer_secret,access_token,access_token_secret = self.keys_and_tokens[screen_name]["consumer_key"],self.keys_and_tokens[screen_name]["consumer_secret"],self.keys_and_tokens[screen_name]["access_token"],self.keys_and_tokens[screen_name]["access_token_secret"]
        self.api = oauth_login(consumer_key,consumer_secret,access_token,access_token_secret)
        self.screen_name = screen_name
        self.followers = self.api.followers_ids(screen_name)
        self.following = self.api.friends_ids(screen_name)
        self.MAX_UNFOLLOW = 1000

    def unfollow_back_who_not_folow_me(self, *arg):
        # Unfollow users that don't follow you back.
        print('**************** Starting to unfollow users ****************')
        # makes a new list of users who don't follow you back.
        non_mutuals = set(self.following) - set(self.followers)
        total_unfollowed = 0

        for f in non_mutuals:
            try:
                account_screen_name = str(self.api.get_user(f).screen_name).lower()
                if account_screen_name in self.accounts_to_follow:
                    # print(f'Did not unfollow: {account_screen_name}')
                    continue
                # unfollows non follower.
                self.api.destroy_friendship(f)
                total_unfollowed += 1
                print(f'Unfollowed [{account_screen_name}]')
                sleep(30)

                if total_unfollowed % 10 == 0:
                    print('---- [' + str(total_unfollowed) + ' users unfollowed so far.] ----')
                    sleep(60)
                if total_unfollowed==self.MAX_UNFOLLOW:
                    print('---- [Unfollowed max number of users, now exiting...] ----')
                    break
                if total_unfollowed == 100:
                    sleep(600)
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                print('---- Error: '+ str(e) + ' ----\n')
                continue
        print("**************** Complete! ****************")
        print("**************** Total number of users unfollowed: " + str(total_unfollowed) + ' ****************\n')

    # FUTURE EDIT: just use self.following instead of non_mutuals
    def unfollow_unspecified_accounts(self, *arg):
        # Unfollow users that aren't specific in the file.
        print('**************** Starting to unfollow users ****************')
        # makes a new list of users who don't follow you back.
        non_mutuals = set(self.following) - set(self.followers)
        total_unfollowed = 0

        for f in self.following:
            try:
                account_screen_name = str(self.api.get_user(f).screen_name).lower()
                if account_screen_name in self.accounts_to_follow:
                    # print(f'Did not unfollow: {account_screen_name}')
                    continue
                # unfollows non follower.
                self.api.destroy_friendship(f)
                total_unfollowed += 1
                print(f'Unfollowed [{account_screen_name}]')
                sleep(10)

                if total_unfollowed % 10 == 0:
                    print('---- [' + str(total_unfollowed) + ' users unfollowed so far.] ----')
                    sleep(60)
                if total_unfollowed==self.MAX_UNFOLLOW:
                    print('---- [Unfollowed max number of users, now exiting...] ----')
                    break
                if total_unfollowed == 100:
                    sleep(600)
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                print('---- Error: '+ str(e) + ' ----\n')
                continue
        print("**************** Complete! ****************")
        print("**************** Total number of users unfollowed: " + str(total_unfollowed) + ' ****************\n')


if __name__ == '__main__':
    screen_name = argv[1]
    bot = TwitterUnfollowBot(screen_name)
    bot.unfollow_unspecified_accounts()

    # for user in keys_and_tokens:
    #     if user == "chadeezy1" or user == "chadle14":
    #         CONSUMER_KEY = keys_and_tokens[screen_name]["consumer_key"]
    #         CONSUMER_SECRET = keys_and_tokens[screen_name]["consumer_secret"]
    #         ACCESS_TOKEN = keys_and_tokens[screen_name]["access_token"]
    #         ACCESS_SECRET = keys_and_tokens[screen_name]["access_token_secret"]
    #
    #         twitterBot = TwitterBot()
    #         twitterBot.unfollow_back_who_not_folow_me()


# python unfollow.py "aikoharunoo"
# python unfollow.py "chazeichazy"
# python unfollow.py "pestermutant"
# python unfollow.py "mergecook"
# python unfollow.py "officialchidori"
