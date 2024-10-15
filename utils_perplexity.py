from openai import OpenAI
import streamlit as st

YOUR_API_KEY = "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"

def provide_online_checks(prompt):
    ''' This function uses perplexity api to fetch the latest content as per prompt from internet'''
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are an artificial intelligence assistant and you need to "
                "engage in a helpful, detailed, polite conversation with a user."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    client = OpenAI(api_key=YOUR_API_KEY, base_url="https://api.perplexity.ai")

    # chat completion without streaming
    response = client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=messages,
    )
    message = response.choices[0].message.content
    return message
