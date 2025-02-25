import time
import random
import tweepy
import threading
import schedule
from groq import Groq
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="CyberpsychAI",
    layout="centered"
)

st.title('CyberpsychAI')
st.markdown("*Thinking something interesting...*")

ACCESS_KEY = st.secrets["general"]["ACCESS_KEY"]
ACCESS_SECRET = st.secrets["general"]["ACCESS_SECRET"]
CONSUMER_KEY = st.secrets["general"]["CONSUMER_KEY"]
CONSUMER_SECRET = st.secrets["general"]["CONSUMER_SECRET"]
BEARER_TOKEN = st.secrets["general"]["BEARER_TOKEN"]
GROQ_API_KEY = st.secrets["general"]["GROQ_API_KEY"]

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
llm = Groq(api_key=GROQ_API_KEY)  # LLM initialization

rivals = ['MistralAI','ChatGPTapp','deepseek_ai','AnthropicAI','GeminiApp','github','MSFTCopilot','Apple']

model_name = "llama3-8b-8192"

psychs = ['Artifical Intelligence', 'Philosophy', 'Financial Advices']

prompt = f"""
You are an expert on the topic of {random.choice(psychs)}, tell me a funny or uncommon fact about
it in less than 250 characters. Your response should be precise, avoid using any unnecessary words.
"""

roast = """
You are a professional comedian. {} is your rival Artifical Intelligence company.
Roast them in less than 250 words. The context is {}.
"""
# Free-tier sends atmost of 17 requests a day, so plan


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

def tweet_job():
    schedule.every(120).minutes.do(tweet)

def generate_post_text():
    tweet = llm.chat.completions.create(
        messages=[
            {
                'role':'system',
                'content': prompt
            }
        ],
        model=model_name,
    )
    return tweet.choices[0].message.content

def generate_reply_text(username, context):
    reply = llm.chat.completions.create(
        messages=[
            {
                'role':'system',
                'content': roast.format(username, context)
            }
        ],
        model=model_name,
    )
    return reply.choices[0].message.content

def tweet():
    try:
        sampletweet = generate_post_text()
        
        post_result = newapi.create_tweet(text=sampletweet)
        print("Just Tweeted!")
    
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

if __name__ == "__main__":
    tweet_job()
    task = threading.Thread(target=run_scheduler)
    task.start()