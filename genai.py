import os
import requests
from bs4 import BeautifulSoup
import streamlit as st
from openai import OpenAI

class GenAI:
    def __init__(self):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    def generate_text(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content

    def display_tweet(self, topic, df, engagement_summary):
        if topic.startswith("http"):
            try:
                html = requests.get(topic).text
                soup = BeautifulSoup(html, "html.parser")
                topic_text = soup.title.string if soup.title else topic
            except:
                topic_text = topic
        else:
            topic_text = topic

        prompt = f"Using the voice of the following user's tweets and this engagement analysis:\n\n{engagement_summary}\n\nWrite a new tweet on the topic: {topic_text}\n\nHere are some sample tweets:\n"
        for _, row in df[['text', 'engagement']].head(10).iterrows():
            prompt += f"Tweet: {row['text']}\nEngagement: {row['engagement']:.4f}\n"

        tweet_text = self.generate_text(prompt)

        return f'''
        <div style="background:#15202B;padding:20px;border-radius:10px;color:white;font-family:sans-serif;">
            <p style="font-size:1.2em;">{tweet_text}</p>
            <p style="color:#8899A6;font-size:0.9em;">Generated Persona Tweet</p>
        </div>
        '''

