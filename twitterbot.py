import tweepy
import time
import json
import csv
import re
import random
import threading
import sys

from progress.spinner import MoonSpinner
from collections import Counter
from datetime import datetime
from follow import TwitterFollowBot

def oauth_login(consumer_key,consumer_secret,access_token,access_token_secret):
    # Switch to application authentication - application-only authentication allows for 450 queries every 15 minutes
    # auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    # api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Setting up new api wrapper, using authentication only
    # User-authentication allows for 180 queries per access token every 15 minutes
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret) #Pass our consumer key and consumer secret to Tweepy's user authentication handler
    auth.set_access_token(access_token, access_token_secret) #Pass our access token and access secret to Tweepy's user authentication handler
    api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Creating a twitter API wrapper using tweepy
    return api

class StreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        self.me = api.me()
        self.restart = False # Mark true when you want to restart the stream
        self.giveaway_keywords = ["win ","winn","giv","enter","retweet","key","free","copy","copies","gift","random","chance"]
        # Dictionary that holds all the information about each account
        with open('keys_and_tokens.json') as f:
            self.keys_and_tokens = json.load(f)
        # Dictionary that holds all the accounts I should be following
        with open('accounts_to_follow.json') as f:
            self.accounts_to_follow = set(json.load(f)["accounts_to_follow"])
        self.initial_amount_of_users_following = len(self.accounts_to_follow)
        # print(f"Number of accounts I'm currently following: {self.initial_amount_of_users_following}")
        # Reads in a file of random comments to comment on statuses with
        with open("comments.txt",'r',encoding="utf8") as f:
            self.comments = f.read().split('\n')

    # Prints a progress spinner to show progress: https://towardsdatascience.com/a-complete-guide-to-using-progress-bars-in-python-aa7f4130cda8
    def progress_spinner(self, tweet_author):
        # If I ever want the spinner to work simultaneously with operations: https://stackoverflow.com/questions/13547921/python-run-a-progess-bar-and-work-simultaneously
        with MoonSpinner(f'Working on a new tweet from [{tweet_author}]...') as bar:
            for i in range(400):
                time.sleep(0.05)
                bar.next()
        print()

    # Stops stream in the event of a error
    def on_error(self, status_code):
        if status_code == 420:
            print(f"Encountered streaming error {str(status_code)}, going to take a 1 hour break.")
            time.sleep(3600)
            return False

    # Filters out tweets based on certain criteria (no retweets, etc.)
    def from_creator(self, status):
        if hasattr(status, 'retweeted_status'):
            return False
        elif status.in_reply_to_status_id != None:
            # Someone is just replying/commenting on a status
            return False
        elif status.in_reply_to_screen_name != None:
            # Someone just tagged a user in a tweet
            return False
        elif status.in_reply_to_user_id != None:
            return False
        else:
            return True

    # Writes all accounts I'm following to file for future use.
    def write_to_file(self):
        # Don't restart the stream unless you're following at least 20 new users
        if len(self.accounts_to_follow) - self.initial_amount_of_users_following > 10:
            print(f"New amount of users im now following: {len(self.accounts_to_follow)}")
            accounts_to_follow_dict = {"accounts_to_follow":list(self.accounts_to_follow),"total_accounts":len(self.accounts_to_follow)}
            with open("accounts_to_follow.json", 'w') as outfile:
                json.dump(accounts_to_follow_dict, outfile, sort_keys=True, indent=2)
            # If I followed new users, then restart the stream so I could stream them as well
            self.restart = True
            print("File overwrite complete.")

    # Likes the tweet
    def like_status(self, temp_status, temp_api, tweet_text):
        try:
            if any(keyword in tweet_text for keyword in ["like"]):
                if not temp_status.favorited:
                    temp_api.create_favorite(temp_status.id)
                    return Counter({"Liked:":1})
                else:
                    return Counter({"Already Liked:":1})
            else:
                return Counter({})
        except tweepy.error.TweepError as e:
            return Counter({"Liked Errors ❌:":1})

    # Retweets the tweet
    def retweet_status(self, temp_status, temp_api, tweet_text):
        try:
            # If the substring "rt" is inside the tweet, then check that it isn't part of a word and is its own word
            if ("retweet" in tweet_text) or ("rt" in tweet_text and "rt" in re.sub(r"[^a-zA-Z0-9]+", ' ', tweet_text).split(' ')):
                if not temp_status.retweeted:
                    temp_api.retweet(temp_status.id)
                    return Counter({"Retweeted:":1})
                else:
                    return Counter({"Already Retweeted:":1})
            else:
                return Counter({})
        except tweepy.error.TweepError as e:
            return Counter({"Retweeted Errors ❌:":1})

    # Follows all mentioned users
    def follow_mentioned_users(self, temp_status, temp_api, tweet_text):
        try:
            new_users_followed = []
            # Only follow accounts if asked to do so and there are actually people I need to follow
            if ("follow" in tweet_text) and (len(temp_status.entities["user_mentions"]) > 0):
                for user in temp_status.entities["user_mentions"]:
                    # Checks whether or not I'm already following the user
                    friendship = temp_api.show_friendship(source_id=temp_api.me().id,target_id=user['id'])
                    if (not friendship[0].following):
                        temp_api.create_friendship(user['id'])
                        time.sleep(5)
                        new_users_followed.append(user['screen_name'])
                        self.accounts_to_follow.add(user['screen_name'].lower())
                if len(new_users_followed) == 0:
                    return Counter({"No One New to Follow:":1})
                # return f"Followed {new_users_followed} ✅ " # In case I want to see the new users followed
                return Counter({"Followed:":1})
            else:
                return Counter({})
        except tweepy.error.TweepError as e:
            print(f'error in follow func: {e}')
            return Counter({"Followed Errors ❌:":1})

    # Tags users in the comments
    def tag_users(self, temp_status, temp_api, tweet_text, screen_name):
        try:
            if any(keyword in tweet_text for keyword in ["tag "]):
                comment = f"@{temp_status.user.screen_name} "
                # Get the number of people the tweet is asking you to tag
                tag_requirement = tweet_text.split("tag ")[1]
                number_of_people_to_tag = 1
                if any(keyword in tag_requirement for keyword in ["2 friend","two friend"]):
                    number_of_people_to_tag = 2
                elif any(keyword in tag_requirement for keyword in ["3 friend","three friend"]):
                    number_of_people_to_tag = 3
                # Twitter API requires you to only include 1 mention per user interaction
                for person_to_tag in range(0,number_of_people_to_tag):
                    temp_comment = comment + f"{self.keys_and_tokens[screen_name]['person_to_tag'][person_to_tag]} "
                    temp_api.update_status(temp_comment,in_reply_to_status_id=temp_status.id)
                return Counter({"Tagged:":1})
            else:
                return Counter({})
        except tweepy.error.TweepError as e:
            print(f'error in tag func: {e}')
            return Counter({"Tagged Errors ❌:":1})

    # Leaves a comment on what the tweet is specifically asking for
    def comment_on_status(self, temp_status, temp_api, tweet_text):
        try:
            if any(keyword in tweet_text for keyword in ["comment","reply"]):
                # Hashtags won't show automatically if status is truncated
                if temp_status.truncated:
                    temp_status = temp_api.get_status(temp_status.id_str, tweet_mode='extended')
                tweet_author = temp_api.get_status(temp_status.id).user.screen_name
                comment = f"@{tweet_author} "
                if len(temp_status.entities["hashtags"]) == 0:
                    print('0 hashtags')
                    double_quotes_found = True
                    # Sometimes tweets asks you to comment a specific thing down
                    specific_comment = re.findall(r'"([^"]*)"', tweet_text)
                    # Search for single quotes if nothing in double quotes was found
                    if specific_comment == []:
                        specific_comment = re.findall(r"'([^']*)'", tweet_text)
                        double_quotes_found = False
                    # If anything was found at all
                    # if specific_comment != [] and double_quotes_found:
                    #     comment += specific_comment[0].replace('"', '').replace("'", '')
                    # elif specific_comment != [] and not double_quotes_found:
                    #     comment += specific_comment[0].replace("'", "").replace('"', '')
                    if specific_comment != []:
                        comment += specific_comment[0]
                    else: # Chooses a random comment to reply to the tweet
                        comment += random.choice(self.comments)
                else:
                    # Adds each hashtag to the comment
                    for hashtag in temp_status.entities["hashtags"]:
                        comment += f"#{hashtag['text']} "
                temp_api.update_status(comment,in_reply_to_status_id=temp_status.id)
                return Counter({"Commented:":1})
            else:
                return Counter({})
        except tweepy.error.TweepError as e:
            print(f'error in comment func: {e}')
            return Counter({"Commented Errors ❌:":1})

    # If a status is a quoted status, then change the working status to the quoted status
    def check_is_quote_status(self, status, tweet_text, tweet_author):
        if (status.is_quote_status):
            new_status = status.quoted_status
            new_tweet_text = new_status.text.lower() if (not new_status.truncated) else new_status.extended_tweet['full_text'].lower()
            # new_tweet_text = new_status.text.lower() if (not new_status.truncated) else new_status.full_text.lower()
            # hasattr(status,"extended_tweet") use this instead
            # new_tweet_text = new_status.text.lower()
            new_tweet_author = tweet_author + f"- EXECUTING ON QUOTED STATUS OF [{new_status.user.screen_name}]"
            return new_status,new_tweet_text,new_tweet_author
        else:
            return status,tweet_text,tweet_author

    # Runs all neccessary operations and returns a message on what was done
    # 1 FUTURE EDIT TO WORK ON
    def execute_operations(self, temp_status, temp_api, tweet_text):
        # single_user_completed_message = ""
        single_user_completed_counter = Counter({"Liked:":0,"Retweeted:":0,"Followed:":0,"Tagged:":0,"Commented:":0,
                                                "Liked Errors ❌:":0,"Retweeted Errors ❌:":0,"Followed Errors ❌:":0,
                                                "Tagged Errors ❌:":0,"Commented Errors ❌:":0,
                                                "Already Executed:":0})
        # Likes the tweet
        like_counter = self.like_status(temp_status, temp_api, tweet_text)
        # Retweets the tweet
        retweet_counter = self.retweet_status(temp_status, temp_api, tweet_text)
        # If tweet has already been liked/retweeted, then don't try to do anything else again
        if like_counter == Counter({'Liked Errors ❌:': 1}) or retweet_counter == Counter({'Retweeted Errors ❌:': 1}):
            return Counter({})
        # Follows all mentioned users
        follow_counter = self.follow_mentioned_users(temp_status, temp_api, tweet_text)
        # Tags users
        tag_counter = self.tag_users(temp_status, temp_api, tweet_text, temp_api.me().screen_name.lower())
        # Comments on the tweet
        comment_counter = self.comment_on_status(temp_status, temp_api, tweet_text)
        # Returns a Counter of every operation that was executed (max values of each key is 1)
        # print(f"counter objects: {like_counter} + {retweet_counter} + {follow_counter} + {tag_counter} + {comment_counter}")
        single_user_completed_counter += like_counter + retweet_counter + follow_counter + tag_counter + comment_counter
        return(single_user_completed_counter)

    # Goes through each of my accounts and begins operating on given tweets
    def login_to_all_accounts(self, status, tweet_text):
        tweet_author = f"Tweet by: [{status.user.screen_name}] "
        # Sets parameters to quoted status attributes if it is a quoted status
        new_status,new_tweet_text,new_tweet_author = self.check_is_quote_status(status, tweet_text, tweet_author)
        # Wait a little after tweet is made before doing anything
        time.sleep(random.randint(5,10))
        # Keeps track of how many accounts were successful in executing operations
        operation_completed_counter = Counter({"Liked:":0,"Retweeted:":0,"Followed:":0,"Tagged:":0,"Commented:":0,"Errors ❌:":0,
                                               "Already Liked:":0,"Already Retweeted:":0,"No One New to Follow:":0})
        # Sets the current time the tweet was streamed in
        current_time = datetime.now().strftime("%I:%M %p")
        # Checks if the tweet is giving something away or not
        if any(keyword in new_tweet_text for keyword in self.giveaway_keywords):
            # Prints out a progress loader
            # self.progress_spinner(status.user.screen_name)
            # Goes through each of my accounts and executes operations
            for screen_name in self.keys_and_tokens:
                consumer_key,consumer_secret,access_token,access_token_secret = self.keys_and_tokens[screen_name]["consumer_key"],self.keys_and_tokens[screen_name]["consumer_secret"],self.keys_and_tokens[screen_name]["access_token"],self.keys_and_tokens[screen_name]["access_token_secret"]
                temp_api = oauth_login(consumer_key,consumer_secret,access_token,access_token_secret) # You only get 180 requests per 15 mins: temp_api.rate_limit_status()["resources"]["application"]["/application/rate_limit_status"]
                try:
                    operation_completed_counter += self.execute_operations(new_status, temp_api, new_tweet_text)
                    # Take a break in between accounts so it doesn't seem like my accounts are related, but skip the break if it's the last account to run
                    if not self.keys_and_tokens[screen_name]['final_account_to_run']:
                        time.sleep(random.randint(10,20))
                except Exception as e:
                    print(f"Error in [login_to_all_accounts] function for [{screen_name}]: {str(e)}\n")
                    continue
            if list(operation_completed_counter.elements()) != []:
                print("--------------------------------------------------------------------------------------")
                # Shows you the tweet you're operating on and what was done
                print(f"{new_tweet_author} @ {current_time}")
                print(f"Tweet ID: {new_status.id}")
                print(new_tweet_text)
                print("[✅ ALL ACCOUNTS COMPLETED ✅ - ",end='')
                for key,value in operation_completed_counter.items():
                    print(key,value,end=" ")
                print("]\n--------------------------------------------------------------------------------------")
                # Keep record of status ids so you can get random comments from them
                # with open("tweet_ids.txt", "a+") as f:
                #     f.write(str(status.id)+"\n")
                # Writes all newly followed accounts to file (if any)
                # self.write_to_file()

    # Runs a check on new tweets as they come in
    # FUTURE EDIT: make this function as bare bones as possible
    def on_status(self, status):
        # Checks to see if the tweet isn't a retweet or a reply to someone else
        if self.from_creator(status):
            try:
                tweet_text = status.text.lower() if (not status.truncated) else status.extended_tweet['full_text'].lower()
                # If it's the tweet has enough content or its quoted tweet is a giveaway, then operate on it
                # FUTURE EDIT: add requirement for kw if tweets longer than 70
                if (len(tweet_text) > 70) or (status.is_quote_status) and ("winner" not in tweet_text):
                    # Running with a new thread so it doesn't clog up the stream: https://stackoverflow.com/questions/39237420/how-to-thread-a-tweepy-stream
                    d = threading.Thread(target=self.login_to_all_accounts,args=(status,tweet_text,))
                    d.start()
                # else:
                #     print(f"Ignored a tweet from [{status.user.screen_name}]\n")
            except tweepy.error.TweepError as e:
                print('Error caught inside [on_status] function')
                print(e)
        # Restarts stream after new users are added to the following-list
        if (self.restart):
            return False

# Starts the stream and keeps it going: https://github.com/tweepy/tweepy/issues/1053
def start_stream(stream, following, screen_name):
    try:
        print('Streaming now...\n')
        stream.filter(follow=following,stall_warnings=True)
        print('Stream restarting...')
    except KeyboardInterrupt:
        # If I manually kill the program, I want to add the new users I followed to file for next time.
        print("\nKeyboard Interruption - ",end='')
        # follow_bot = TwitterFollowBot(screen_name)
        # follow_bot.add_accounts_to_file()
        sys.exit(0)
    except Exception as e:
        stream.disconnect()
        print(f"Fatal exception: {str(e)}")
        time.sleep(1800)
        start_stream(stream, following, screen_name)

# Searches Twitter for tweets relating to giveaways and fulfills requirements to win baby!
def main(screen_name):
    # Logs into the account of choice and streams that specific account's following-list
    with open('keys_and_tokens.json') as f:
      keys_and_tokens = json.load(f)
    consumer_key,consumer_secret,access_token,access_token_secret = keys_and_tokens[screen_name]["consumer_key"],keys_and_tokens[screen_name]["consumer_secret"],keys_and_tokens[screen_name]["access_token"],keys_and_tokens[screen_name]["access_token_secret"]
    api = oauth_login(consumer_key,consumer_secret,access_token,access_token_secret)
    while True:
        # You only get 15 requests per 15 minutes, so take a break if you're getting too close
        if api.rate_limit_status()["resources"]["friends"]["/friends/ids"]["remaining"] < 5:
            time.sleep(900)
        # Sets up streaming object to listen for tweets
        with open('account_ids.json') as f:
            following = json.load(f)["account_ids"]
        # following = [str(i) for i in api.friends_ids(screen_name)] # 15 requests per 15 minutes
        streamListener = StreamListener(api)
        stream = tweepy.Stream(auth=api.auth,listener=streamListener,tweet_mode='extended',timeout=90)
        start_stream(stream, following, screen_name)

if __name__ == '__main__':
    screen_name = sys.argv[1]
    main(screen_name)
    # python twitterbot.py pestermutant
