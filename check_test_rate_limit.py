auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):

	with open('fetched_tweets.txt','a') as tf:
            tf.write(status.full_text.encode('utf-8') + '\n')
	
        print(status.text)

    def on_error(self, status):
	print("Error Code : " + status)

    def test_rate_limit(api, wait=True, buffer=.1):
	    """
	    Tests whether the rate limit of the last request has been reached.
	    :param api: The `tweepy` api instance.
	    :param wait: A flag indicating whether to wait for the rate limit reset
		         if the rate limit has been reached.
	    :param buffer: A buffer time in seconds that is added on to the waiting
		           time as an extra safety margin.
	    :return: True if it is ok to proceed with the next request. False otherwise.
	    """
	    #Get the number of remaining requests
	    remaining = int(api.last_response.getheader('x-rate-limit-remaining'))
	    #Check if we have reached the limit
	    if remaining == 0:
		limit = int(api.last_response.getheader('x-rate-limit-limit'))
		reset = int(api.last_response.getheader('x-rate-limit-reset'))
		#Parse the UTC time
		reset = datetime.fromtimestamp(reset)
		#Let the user know we have reached the rate limit
		print "0 of {} requests remaining until {}.".format(limit, reset)

		if wait:
		    #Determine the delay and sleep
		    delay = (reset - datetime.now()).total_seconds() + buffer
		    print "Sleeping for {}s...".format(delay)
		    sleep(delay)
		    #We have waited for the rate limit reset. OK to proceed.
		    return True
		else:
		    #We have reached the rate limit. The user needs to handle the rate limit manually.
		    return False 

	    #We have not reached the rate limit
	    return True

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener , tweet_mode='extended')

 
myStream.filter(track=['#bitcoin'],async=True)