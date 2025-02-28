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
st.markdown("*Tweeting something interesting...*")

LIMIT = 2 # Daily tweet limit

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
scheduler_thread_lock = threading.Lock() # avoids multiple threads to be created
scheduler_running = False

post_times = ["04:41","01:30","03:30","05:30","07:30","09:30",
              "11:30","13:30","15:30","17:30","19:30","21:30","23:30"]  # Instance timezone is UTC

# rivals = ['MistralAI','ChatGPTapp','deepseek_ai','AnthropicAI','GeminiApp','github','MSFTCopilot','Apple']

model_name = "llama3-8b-8192"

psychs = ['Philosophy','Stoicism','Life Advices','Neuroscience']

# Free-tier sends atmost of 17 requests a day, so plan
logging.basicConfig(level=logging.INFO)


def run_scheduler():
    global scheduler_running
    scheduler_running = True
    while scheduler_running:
        schedule.run_pending()
        time.sleep(5) # allows the scheduler to run every 5 seconds w/o overhead

def tweet_job():
    global scheduler_thread, scheduler_running
    with scheduler_thread_lock:
        if scheduler_thread is None or not scheduler_thread.is_alive():
            logging.info("Initializing tweet schedule...")

            if not scheduler_running:  # Avoid unnecessary clears
                schedule.clear()
                for post in post_times:
                    schedule.every().day.at(post).do(tweet)

            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            scheduler_running = True
        else:
            logging.info("Scheduler is already running. No new thread required.")

def generate_post_text():
    topic = random.choice(psychs)

    prompt = f"""
    You are an expert in {topic}. Share a precise insight (under 250 characters) 
    that can improve my perspective on life or human behavior. Keep it concise and impactful, avoiding unnecessary words.
    """

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
    global LIMIT
    try:
        logging.info("Attempting to tweet...")
        if LIMIT > 0:
            sampletweet = generate_post_text()
            post_result = newapi.create_tweet(text=sampletweet)
            logging.info(f"Tweet posted: {post_result.data['id']}")
            LIMIT -= 1
        else:
            raise Exception("Tweet limit reached for the day.")
    except Exception as e:
        logging.error(f"Tweet couldn't be posted: {e}")

tweet_job()