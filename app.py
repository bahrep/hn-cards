import os
import asyncio
import aiohttp
import openai
from flask import Flask, render_template, jsonify

openai.api_key = os.environ["OPENAI_API_KEY"]

app = Flask(__name__)

async def get_top_stories(session):
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    async with session.get(url) as response:
        return await response.json()[:5]

async def get_story_details(session, story_id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    async with session.get(url) as response:
        return await response.json()

async def fetch_top_stories():
    async with aiohttp.ClientSession() as session:
        story_ids = await get_top_stories(session)
        story_details = await asyncio.gather(
            *[get_story_details(session, story_id) for story_id in story_ids]
        )

        # Generate image URLs for each story
        image_urls = await asyncio.gather(
            *[generate_image_url(story['title']) for story in story_details]
        )

        # Combine story details and image URLs
        stories = [
            (story['title'], story['url'], image_url)
            for story, image_url in zip(story_details, image_urls)
        ]

        return stories

async def get_top_stories(session):
    url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
    async with session.get(url) as response:
        story_ids = await response.json()
        return story_ids[:5]

async def generate_image_url(prompt):
    try:
        response = openai.Image.create(
            model="image-alpha-001",
            prompt=prompt,
            n=1,
            size="256x256",
            response_format="url",
        )
        return response['data'][0]['url']
    except Exception as e:
        print(f"Error generating image for prompt '{prompt}': {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/top_stories')
async def top_stories():
    stories = await fetch_top_stories()
    return jsonify(stories)

if __name__ == '__main__':
    app.run(debug=True)