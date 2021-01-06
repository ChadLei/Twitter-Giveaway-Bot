import tweepy
import json
import time
import re
import random
import argparse
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

class ExecuteOperations:
    def __init__(self, quick=False):
        parser = argparse.ArgumentParser()
        parser.add_argument('q',type=bool,default=False,nargs='?',help='Command to complete operations immediately')
        self.quick = parser.parse_args().q
        self.tweet_urls = []
        self.status_ids = []
        with open('keys_and_tokens.json') as f:
            self.keys_and_tokens = json.load(f)
        with open('accounts_to_follow.json') as f:
            self.accounts_to_follow = json.load(f)["accounts_to_follow"]

    # Writes all accounts to file for future use.
    def write_to_file(self):
        accounts_to_follow_dict = {"accounts_to_follow":list(set(self.accounts_to_follow)),"total_accounts":len(list(set(self.accounts_to_follow)))}
        with open("accounts_to_follow.json", 'w') as outfile:
            json.dump(accounts_to_follow_dict, outfile, sort_keys=True, indent=2)

    # Stores user-inputted tweet urls.
    def get_user_input(self):
        print("Enter a url in the following format:\n[https://twitter.com/{USERNAME}/status/{NUMBER}]\n")
        while True:
            url = input("Tweet URL: ")
            if url == '':
                break
            self.tweet_urls.append(url) if re.search('/status/(\d+)', url) != None else print("Invalid URL... try again")
        self.status_ids = [re.search('/status/(\d+)', url).group(1) for url in self.tweet_urls]

    # Likes the tweet
    def like_status(self, temp_api, status_id):
        if not temp_api.get_status(status_id).favorited:
            try:
                temp_api.create_favorite(status_id)
                return "Liked ✅ "
            except tweepy.error.TweepError as e:
                # return "Liked ✅ "
                return str(e)
        else:
            return "Already Liked ✅ "

    # Retweets the tweet
    def retweet_status(self, temp_api, status_id, temp_status):
        try:
            if any(keyword in temp_status.full_text.lower() for keyword in [" rt","rt ","-rt"," rt ","rt\n","retweet"]):
                if not temp_api.get_status(status_id).retweeted:
                    temp_api.retweet(status_id)
                    return "Retweeted ✅ "
                else:
                    return "Already Retweeted ✅ "
            else:
                return ""
        except tweepy.error.TweepError as e:
            # return "Already Retweeted ✅ "
            return str(e)

    # Follows all mentioned users
    def follow_mentioned_users(self, temp_api, temp_status):
        try:
            if ("follow" in temp_status.full_text.lower()): # Only follow accounts if asked to do so
                new_users_followed = []
                # Adds the author just in case I don't already follow them
                temp_status.entities["user_mentions"].append(temp_status.user._json)
                for user in temp_status.entities["user_mentions"]:
                    # Checks whether or not I'm already following the user
                    friendship = temp_api.show_friendship(source_id=temp_api.me().id,target_id=user['id'])
                    if (not friendship[0].following):
                        temp_api.create_friendship(user['id'])
                        new_users_followed.append(user['screen_name'])
                        self.accounts_to_follow.append(user['screen_name'].lower())
                # Don't print anything if no one new was followed
                if len(new_users_followed) == 0:
                    return ""
                return f"Followed {new_users_followed} ✅ "
            return ""
        except tweepy.error.TweepError as e:
            return f"Already Followed {new_users_followed} ✅ "

    # Tags users in the comments
    def tag_users(self, temp_api, status_id, temp_status, screen_name):
        try:
            if any(keyword in temp_status.full_text.lower() for keyword in ["tag","reply"]):
                comment = f"@{temp_status.user.screen_name} {self.keys_and_tokens[screen_name]['person_to_tag']}"
                temp_api.update_status(comment,in_reply_to_status_id=status_id)
                return "Tagged ✅ "
            return ""
        except tweepy.error.TweepError as e:
            return "Already Tagged ✅ "

    # Leaves a comment on what the tweet is specifically asking for
    def comment_on_status(self, temp_api, status_id, temp_status):
        try:
            if any(keyword in temp_status.full_text.lower() for keyword in ["comment","reply"]):
                tweet_author = temp_api.get_status(status_id).user.screen_name
                comment = f"@{tweet_author} "
                # Adds each hashtag to the comment
                for hashtag in temp_status.entities['hashtags']:
                    comment += f"#{hashtag['text']} "
                temp_api.update_status(comment,in_reply_to_status_id=status_id)
                return "Commented ✅ "
            return ""
        except tweepy.error.TweepError as e:
            return "Already Commented ✅ "

    def execute_operations(self):
        for screen_name in self.keys_and_tokens:
            print(f'Executing as [{screen_name.upper()}] - ',end="")
            # Logs into each individual account in order to complete tasks
            completed_tasks_message = ""
            consumer_key,consumer_secret,access_token,access_token_secret = self.keys_and_tokens[screen_name]["consumer_key"],self.keys_and_tokens[screen_name]["consumer_secret"],self.keys_and_tokens[screen_name]["access_token"],self.keys_and_tokens[screen_name]["access_token_secret"]
            temp_api = oauth_login(consumer_key,consumer_secret,access_token,access_token_secret)
            # Goes through all user-inputted tweets and completes the neccessary tasks
            for status_id in self.status_ids:
                # If the given tweet is a quoted tweet, then operate on the quoted tweet instead
                temp_status = temp_api.get_status(status_id,tweet_mode="extended")
                if (temp_status.is_quote_status):
                    status_id = temp_status.quoted_status_id
                    temp_status = temp_api.get_status(status_id,tweet_mode="extended")
                # Adds a confirmation message for every task completed
                completed_tasks_message += self.like_status(temp_api, status_id)
                completed_tasks_message += self.retweet_status(temp_api, status_id, temp_status)
                completed_tasks_message += self.follow_mentioned_users(temp_api, temp_status)
                completed_tasks_message += self.tag_users(temp_api, status_id, temp_status, screen_name)
                completed_tasks_message += self.comment_on_status(temp_api, status_id, temp_status)
            # Prints message showing what operations were completed
            print(completed_tasks_message)
            # Don't take a break if it's the final account
            if (not self.keys_and_tokens[screen_name]['final_account_to_run']) and (not self.quick):
                time.sleep(random.randint(30,45))

    # Main function to run.
    def start(self):
        self.get_user_input()
        self.execute_operations()
        self.write_to_file()



if __name__ == '__main__':
    bot = ExecuteOperations()
    bot.start()







#
