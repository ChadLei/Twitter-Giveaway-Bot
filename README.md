# Twitter Giveaway Bot

A script that listens to your choice of accounts for giveaways and raffles and enters them according to the requirements of the tweet (like, retweet, comment, tag your friends, etc.)

## Inspiration
https://qz.com/476914/i-built-a-twitter-bot-that-entered-and-won-1000-online-contests-for-me/

## Requirements
1. Must have a developer account for the account(s) you want to run this script with.
2. This script uses the Tweepy Library: https://www.tweepy.org/
3. Contact me for the format of the keys/tokens file!

## Usage
#### To run bot:
#### Run the following command and replace {YOUR_ACCOUNT_NAME} with your personal account.
```python
python twitterbot.py YOUR_ACCOUNT_NAME
```

## Useful links:
##### home_timeline for when you want to get 20 of the most recent statuses from my PERSONAL timeline
- https://www.geeksforgeeks.org/python-api-home_timeline-in-tweepy/
- notes:
- home_timeline: 15 requests per 15 min window (1 request / min)
- user_timeline: 900 requests per 15 min window (60 request / min)
##### https://unionmetrics.com/resources/how-to-use-advanced-twitter-search-queries/
