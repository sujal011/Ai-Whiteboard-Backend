import json
from dotenv import load_dotenv
import os
from prompt2 import get_prompt

load_dotenv()
groq_api_key = os.getenv("GROQ_API")
from groq import Groq

client = Groq(api_key=groq_api_key)


def analyze_image(img: str, dict_of_vars: str):
    prompt=get_prompt()
    completion = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img
                    }
                }
            ]
        }
    ],
    temperature=1,
    max_tokens=2048,
    top_p=1,
    stream=False,
    response_format={"type": "json_object"},
    stop=None,
)
    print(completion.choices[0].message.content)
    return json.loads(completion.choices[0].message.content)