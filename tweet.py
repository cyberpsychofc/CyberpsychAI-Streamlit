import streamlit as st
import random
import tweepy
from generate_tweet import generate_post_text, generate_reply_text

ACCESS_KEY = st.secrets["general"]["ACCESS_KEY"]
ACCESS_SECRET = st.secrets["general"]["ACCESS_SECRET"]
CONSUMER_KEY = st.secrets["general"]["CONSUMER_KEY"]
CONSUMER_SECRET = st.secrets["general"]["CONSUMER_SECRET"]
BEARER_TOKEN = st.secrets["general"]["BEARER_TOKEN"]

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(
    ACCESS_KEY,
    ACCESS_SECRET,
)

newapi = tweepy.Client(
    bearer_token= BEARER_TOKEN,
    access_token= ACCESS_KEY,
    access_token_secret= ACCESS_SECRET,
    consumer_key= CONSUMER_KEY,
    consumer_secret= CONSUMER_SECRET,
)

api = tweepy.API(auth)

rivals = ['MistralAI','ChatGPTapp','deepseek_ai','AnthropicAI','GeminiApp','github','MSFTCopilot','Apple']


def tweet():
    try:
        sampletweet = generate_post_text()
        
        post_result = newapi.create_tweet(text=sampletweet)
    
    except Exception as e:
        print(f"Tweet couldn't be posted because: {e}")

def reply():
    try:
        username = random.choice(rivals)
        tweets = newapi.search_recent_tweets(
            query=f"from:{username} -is:retweet -is:reply", 
            max_results=10, 
            tweet_fields=["id", "text"])
        
        if tweets:
            latest_tweet = random.choice(tweets.data)  
            tweet_id = latest_tweet.id  
            tweet_text = latest_tweet.text  
            newapi.create_tweet(in_reply_to_tweet_id=tweet_id, text=generate_reply_text(username,tweet_text))

    except Exception as e:
        print(f"Reply couldn't be posted because: {e}")