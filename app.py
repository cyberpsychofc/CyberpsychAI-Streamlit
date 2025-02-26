import time
import random
import tweepy
import threading
import schedule
from groq import Groq
import streamlit as st
import logging
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

st.set_page_config(
    page_title="CyberpsychAI",
    layout="centered"
)

st.title('CyberpsychAI')
st.markdown("*Thinking something interesting...*")
log_container = st.empty()

class StreamlitLogHandler(logging.Handler):
    def __init__(self, container):
        super().__init__()
        self.container = container
        self.log_messages = [] 
   
    def emit(self, record):
        log_entry = self.format(record)  
        self.log_messages.append(log_entry)  
        log_text = "\n".join(self.log_messages) 
        self.container.text(log_text)

logger = logging.getLogger("streamlit_logger")
logger.setLevel(logging.INFO)

streamlit_handler = StreamlitLogHandler(log_container)
streamlit_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(streamlit_handler)

streamlit_default_handler = logging.StreamHandler()
streamlit_default_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(streamlit_default_handler)

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

post_times = ["01:30","03:30","05:30","07:30","09:30",
              "11:30","13:30","15:30","17:30","19:30","21:30","23:30"]  # Instance timezone is UTC

# rivals = ['MistralAI','ChatGPTapp','deepseek_ai','AnthropicAI','GeminiApp','github','MSFTCopilot','Apple']

model_name = "llama3-8b-8192"

psychs = ['Philosophy','Stoicism','Life Advices','Emotional Intelligence']

prompt = f"""
You are an expert on the topic of {random.choice(psychs)}, tell me an uncommon fact about
it in less than 250 characters. Your response should be precise, avoid using any unnecessary words.
"""
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
        logging.info(f"Tweet posted: {post_result.data["id"]}")
    except Exception as e:
        logging.error(f"Tweet couldn't be posted: {e}")

tweet_job()

# Ensuring the thread runs only once
if not any(isinstance(thread, threading.Thread) and thread.is_alive() for thread in threading.enumerate()):
    logger.info('CyberpsychAI is online...')
    task = threading.Thread(target=run_scheduler, daemon=True)
    task.start()