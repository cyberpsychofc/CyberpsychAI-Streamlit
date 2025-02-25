import random
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = st.secret["GROQ_API_KEY"]

llm = Groq(api_key=GROQ_API_KEY)  # LLM initialization

psychs = ['Artifical Intelligence', 'Philosophy', 'Financial Advices']

prompt = f"""
You are an expert on the topic of {random.choice(psychs)}, tell me a funny or uncommon fact about
it in less than 250 characters. Your response should be precise, avoid using any unnecessary words.
"""

roast = """
You are a professional comedian. {} is your rival Artifical Intelligence company.
Roast them in less than 250 words. The context is {}.
"""

model_name = "llama3-8b-8192"


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