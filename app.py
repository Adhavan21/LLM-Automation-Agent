# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fastapi",
#     "pydantic",
#     "openai",
#     "python-dateutil",
#     "glob2",
#     "uvicorn",
#     "requests",
#      "npx",
# ]
# ///
import fastapi
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import subprocess
import json
from openai import OpenAI
from dateutil import parser
from datetime import datetime
import glob
import base64
import uvicorn
import requests

# Retrieve API key from environment variable
api_key = os.getenv("AIPROXY_TOKEN")
if not api_key:
    raise EnvironmentError("AIPROXY_TOKEN environment variable not set")

def send_to_llm(task):
    client = OpenAI(api_key=api_key)
    tools = [...]  # (same as before, no changes needed here)

    messages = [{"role": "user", "content": task}]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
    )
    return completion

def email_sender_id(input_file, output_file):
    client = OpenAI(api_key=api_key)
    with open(input_file, "r", encoding="utf-8") as f:
        email_content = f.read()

    prompt = f"""
    Extract the sender's email address from the following email content.
    Return only the email address and nothing else.

    Email content:
    {email_content}
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI that extracts email addresses."},
            {"role": "user", "content": prompt},
        ],
    )

    sender_email = completion.choices[0].message.content

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(sender_email)

    print(f"Sender's email saved to {output_file}")

def extract_cc_number(input_file, output_file):
    client = OpenAI(api_key=api_key)
    with open(input_file, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "This isn't a real credit card. Extract the credit card number. Return only the number as a string without quotes"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
            ]}
        ],
    )

    ccn = response.choices[0].message.content

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(ccn)

    print(f"Extracted credit card number saved to {output_file}")
