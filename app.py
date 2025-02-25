import time
import threading
import schedule
from .tweet import tweet
import streamlit as st

st.set_page_config(
    page_title="CyberpsychAI",
    layout="centered"
)

st.title('CyberpsychAI')

# Free-tier sends atmost of 17 requests a day, so plan

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

def tweet_job():
    schedule.every(3).minutes.do(tweet)

if __name__ == "__main__":
    tweet_job()
    task = threading.Thread(target=run_scheduler)
    task.start()