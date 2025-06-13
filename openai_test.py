from config import api_key
import os
from openai import OpenAI
os.environ["OPENAI_API_KEY"] = api_key

client = OpenAI()

def generate_chatgpt_response(prompt):
    tmpresponse = client.responses.create(
        model="gpt-3.5-turbo",
        instructions="You are a coding assistant that talks like a pirate.",
        input=prompt,
    )
    return tmpresponse

resp = generate_chatgpt_response("when did 2019 capital one cyber incident became public knowledge?")
print(resp.output_text)