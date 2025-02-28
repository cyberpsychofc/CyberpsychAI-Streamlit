import time
import random
import tweepy
import threading
import schedule
from groq import Groq
import streamlit as st
import logging
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

scheduler_thread = None
scheduler_thread_lock = threading.Lock() 

post_times = ["01:54","01:55","01:56","01:57","01:58","01:30","03:30","05:30","07:30","09:30",
              "11:30","13:30","15:30","17:30","19:30","21:30","23:30"]  # Instance timezone is UTC

# rivals = ['MistralAI','ChatGPTapp','deepseek_ai','AnthropicAI','GeminiApp','github','MSFTCopilot','Apple']

model_name = "llama3-8b-8192"

psychs = ['Philosophy','Stoicism','Life Advices','Neuroscience']

prompt = f"""
You are an expert in {random.choice(psychs)}. Share a precise insight (under 250 characters) 
that can improve my perspective on life or human behavior. Keep it concise and impactful, avoiding unnecessary words.
"""

logging.basicConfig(level=logging.INFO)
# Free-tier sends atmost of 17 requests a day, so plan


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

def tweet_job():
    schedule.clear()
    for post in post_times:
        schedule.every().day.at(post).do(tweet)

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

def generate_reply_text(username, context, roast):
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
        logging.info("Attempting to tweet...")
        sampletweet = generate_post_text()
        post_result = newapi.create_tweet(text=sampletweet)
        logging.info(f"Tweet posted: {post_result.data['id']}")
        time.sleep(600)
    except Exception as e:
        logging.error(f"Tweet couldn't be posted: {e}")

tweet_job()

state_lock = threading.Lock() # avoids multiple threads to be created

with scheduler_thread_lock:
    if scheduler_thread is None:
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()