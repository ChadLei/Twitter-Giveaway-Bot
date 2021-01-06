import tweepy
import time
import json
import csv
import re
from sys import argv

from accounts_to_follow import *


with open('keys_and_tokens.json') as f:
  keys_and_tokens = json.load(f)

# Searches Twitter for tweets relating to giveaways and fulfills requirements to win baby!
def main(name,consumer_key,consumer_secret,access_token,access_token_secret):
	# User-authentication allows for 180 queries per access token every 15 minutes
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret) #Pass our consumer key and consumer secret to Tweepy's user authentication handler
	auth.set_access_token(access_token, access_token_secret) #Pass our access token and access secret to Tweepy's user authentication handler
	api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Creating a twitter API wrapper using tweepy

	# Switch to application authentication - application-only authentication allows for 450 queries every 15 minutes
	# auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
	# api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True) #Setting up new api wrapper, using authentication only

	tweetCount = 0 # Count of how many tweets I've gone through so far
	numOfTweets = 3000 # Maximum number of tweets we want to collect
	numberOfTotalTweetsGoneThru = 0
	# search = ("#rttowin OR #giveaway OR (give away) OR giveaway OR (likes and rts) OR (like and retweet) OR (like and rt) OR (retweet to enter) OR (retweet to win) OR (rt to win) OR (chance to win) OR (giving away) OR (win free) OR (win a free) OR (chance to win) -filter:retweets")
	search = ('''
		((likes and rts) OR
		(like and retweet) OR
		(like and rt) OR
		(rt to #win) OR
		(rt to win)) AND

		(a lifetime copy of) OR
		(win a copy of) OR
		(win a lifetime) OR
		(retweet to enter) OR
		(retweet to win) OR
		(chance to win) OR
		(give away) OR
		(giveaway) OR
		(#giveaway) OR
		(giving away) OR
		(#rttowin) OR
		(win free) OR
		(win a free)
		-filter:retweets''')

	# Words to ignore since these actions are too specific at the moment
	wackWords = ['pass royale','v-bucks','follow whoever','retweet with the tag','ping account','adoptme','answer the poll','instagram','facebook','cash',
		'sign up','code','$','bounty reward','coin','give proof','show proof','stream','streamer','staxel','fortnite','twitch', 'survey', 'fill out', 'rsvp',
		'enter here','click to','dm ','battle pass','battlepass','win nothing','help me','#sugar','ikonik','discount 30%','discount 50%','send me a picture',
		'send me a', 'knight ranks', 'for me to win', 'help me win', 'click here', 'share any', 'comment this tweet with a picture', 'draw a', 'followers',
		'royale', ' original tweet', 'pinned tweet', 'yt channel', 'roblox', 'adoptme', 'original post', 'bloxburg', 'keys', 'rank', 'send proof',
		'eon acc', 'vbucks', 'extra lives', 'fake giveaway', 'giving away nothing', 'iptv', 'x1'
	]

	for tweet in tweepy.Cursor(api.search, search, count=100, tweet_mode='extended').items(numOfTweets):
		numberOfTotalTweetsGoneThru += 1
		try:
			# Avoids a account called Bot Spotting that is used to catch bots
			if tweet.user.name == 'Bot Spotting' or 'bot' in tweet.user.name.lower():
				continue

			# Checks tweets for what the user wants us to do in order to be eligible for the giveaway and executes certain actions
			tweetText = tweet.full_text
			if  all(word not in tweetText.lower() for word in wackWords):
				# Keeps track of users that this script has gone through to check for specific accounts (sneaker bot related accounts)
				print("[USERNAME: " + tweet.user.screen_name + "]")
				# with open('usersIWentThrough.csv', 'a') as data_file:
				# 	writer = csv.writer(data_file)
				# 	writer.writerow([tweet.user.screen_name])

				# Checks criteria and acts accordingly
				print(tweetText.lower())
				if 'like' in tweetText.lower():
					tweet.favorite()
					print("---- [Liked] ----")
				if 'retweet' in tweetText.lower() or 'rt' in tweetText.lower():
					tweet.retweet()
					print("---- [Retweeted] ----")
				if 'tag ' in tweetText.lower() or 'tell us' in tweetText.lower() or 'comment' in tweetText.lower() or 'reply' in tweetText.lower():
					userID = tweet.user.screen_name
					comment = "@%s @officialchidori @chazeechazy @ChadLe14 @chadeezy1 i'm done, look yall i dig this im bettin sz 10 US  :)" % (userID)
					api.update_status(comment, tweet.id)
					print("---- [Tagged] ----")
				if 'follow' in tweetText.lower():
					api.create_friendship(tweet.user.id)
					print("---- [Followed: @" + tweet.user.screen_name + "] ----")
					textlist = re.split('[,\s\n]',tweetText.lower())
					for subtext in textlist:
						if subtext.startswith('@') and subtext != str(tweet.user.screen_name).lower():
							try:
								person = subtext.strip('@').strip(',').strip('\n').strip('!')
								personID = api.get_user(person).id # Retrieves user's ID so that Twitter can follow them
								api.create_friendship(personID)
								print("---- [Followed: @" + person + "] ----")
							except:
								print("---- [Couldn't follow: " + subtext + "] ----") # Catches errors when Twitter cannot find specified user to follow
				tweetCount += 1
				print("[Number of tweets " + name + " has gone through: " + str(tweetCount) + ']\n')
				time.sleep(100)
			else:
				# print(tweetText.lower())
				print("---- [Skipped user " + tweet.user.screen_name + " - probably due to tweet containing a wack word] ----\n")
				# time.sleep(5)
		except tweepy.TweepError as e:
			# print('---- Error: '+ str(e[0][0]['message']) + ' ----\n')
			print('---- Error: '+ str(e) + ' ----\n')
			if '429' in str(e):
				time.sleep(4000)
			continue
		except StopIteration:
			print("[I have stopped for some reason....]")
			break
		except UnicodeEncodeError:
			print("[(tweetText.lower() couldn't convert tweet....]")
			continue
	# print(api.rate_limit_status()['resources']['search']) #You can check how many queries you have left using rate_limit_status() method
	# print("[Number of tweets has gone through: " + str(tweetCount) + ']\n')
	print("**************** Complete! ****************")
	print("[Number of tweets liked/retweeted/followed: " + str(tweetCount) + ']\n')
	print("**************** Total number of tweets gone thru: " + str(numberOfTotalTweetsGoneThru) + ' ****************\n')



if __name__ == '__main__':

	print(keys_and_tokens['chazeichazy'])
	# name = argv[1]
	# consumer_key = argv[2]
	# consumer_secret = argv[3]
	# access_token = argv[4]
	# access_token_secret = argv[5]
	# main(name,consumer_key,consumer_secret,access_token,access_token_secret)
	# main("ChadLe14",ChadLe14_consumer_key,ChadLe14_consumer_secret,ChadLe14_access_token,ChadLe14_access_token_secret)
