import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

response = client.responses.create(
    model="gpt-4o",
    input="Latest Bike in Royal Enfield Showroom"
)

print(response.output_text)