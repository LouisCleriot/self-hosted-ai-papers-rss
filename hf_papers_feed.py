#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import os
from pathlib import Path
from urllib.parse import urljoin

# Configuration
TODAY_STR = datetime.now().strftime('%Y-%m-%d')
TARGET_URL = f"https://huggingface.co/papers/date/{TODAY_STR}"
OUTPUT_DIR = Path("/var/www/html")  #nginx html directory on my raspberry pi
OUTPUT_FILENAME = "huggingface_daily_papers.atom"
OUTPUT_PATH = OUTPUT_DIR / OUTPUT_FILENAME
BASE_URL = "https://huggingface.co"
SELF_FEED_URL = "http://192.168.0.195/huggingface_daily_papers.atom"

# Selectors main page
PAPER_SELECTOR = "article.border"                                
TITLE_LINK_SELECTOR = "h3 > a[href^='/papers/']"                  
IMAGE_SELECTOR = "article > a > img[src*='cdn-thumbnails.huggingface.co']" 
VIDEO_SELECTOR = "article > a > video"
UPVOTE_SELECTOR = "div.shadow-alternate > div.leading-none"

# Selectors paper page
ABSTRACT_SELECTOR = "p.text-gray-600"
PUBLISHED_DATE_SELECTOR = "div.pb_10 > div.mb-6 > div"


def generate_feed():
    print(f"Fetching papers from: {TARGET_URL}")

    headers = {
        'User-Agent': 'RaspberryPi-RSS-Generator/1.0 (python-requests; +https://github.com/)'
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return 
    
    soup = BeautifulSoup(response.content, 'lxml')
    
    fg = FeedGenerator()
    fg.title(f"Hugging Face Daily Papers - {TODAY_STR}")
    fg.link(href=TARGET_URL, rel='alternate')
    fg.id("https://huggingface.co/papers")
    fg.subtitle('Daily AI papers digest from Hugging Face, scraped feed.')
    fg.author({'name': "Unofficial Hugging Face Papers Feed"})
    fg.language('en')
    fg.load_extension('media')
    fg.link(href=SELF_FEED_URL, rel='self')
    
    paper_elements = soup.select(PAPER_SELECTOR)
    print(f"Found {len(paper_elements)} paper elements using selector '{PAPER_SELECTOR}'.")
    
    for paper_elem in paper_elements:
        title_link_elem = paper_elem.select_one(TITLE_LINK_SELECTOR)
        image_elem = paper_elem.select_one(IMAGE_SELECTOR)
        video_elem = None
        score_elem = paper_elem.select_one(UPVOTE_SELECTOR)
        
        if not title_link_elem:
            print(f"Warning: Could not find title/link using '{TITLE_LINK_SELECTOR}'")
            continue
        
        paper_title = title_link_elem.get_text(strip=True)
        relative_paper_url = title_link_elem['href']
        absolute_paper_url = urljoin(BASE_URL, relative_paper_url)
        #go to the absolute paper URL 
        try :
            paper_response = requests.get(absolute_paper_url, headers=headers, timeout=30)
            paper_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching paper URL: {e}")
            continue
        
        if not paper_title or not absolute_paper_url:
             print(f"Warning: Missing title or URL for element. Skipping.")
             continue
         
        fe = fg.add_entry()
        fe.title(paper_title)
        fe.link(href=absolute_paper_url)
        fe.id(absolute_paper_url)
        
        absolute_media_url = None
        score = None
        description_parts = []
        
        paper_soup = BeautifulSoup(paper_response.content, 'lxml')      
        abstract_elem = paper_soup.select_one(ABSTRACT_SELECTOR)
        if abstract_elem:
            abstract_text = abstract_elem.get_text(strip=True)
            if abstract_text:
                fe.summary(abstract_text)
        else:
            print(f"Warning: No abstract found using '{ABSTRACT_SELECTOR}' for paper '{paper_title}'.")

        if score_elem:
            score = score_elem.get_text(strip=True)
            print(f"Found score: {score} for '{paper_title}'")
            # Add score to description parts
            if score: # Check if score text is not empty
                 description_parts.append(f'<p>Score: <b>{score}</b></p>')
        else:
             print(f"Note: No score found using '{UPVOTE_SELECTOR}' for paper '{paper_title}'.")

        if image_elem and 'src' in image_elem.attrs:
            absolute_media_url = urljoin(BASE_URL, image_elem['src'])
            mime_type = "image/jpeg" if absolute_media_url.endswith('.jpg') else "image/png"
            medium = "image"
        else: 
            video_elem = paper_elem.select_one(VIDEO_SELECTOR)
            if video_elem and 'src' in video_elem.attrs:
                absolute_media_url = urljoin(BASE_URL, video_elem['src'])
                mime_type = "video/mp4" if absolute_media_url.endswith('.mp4') else "video/webm"
                medium = "video"

        fe.media.content({
            "url": absolute_media_url,
            "type": mime_type,
            "medium": medium,
        })
        
        if description_parts:
            description_html = "".join(description_parts)
            fe.content(description_html, type='html')
        else:
             fe.content(paper_title, type='text')
             
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        fg.atom_file(str(OUTPUT_PATH), pretty=True)
        print(f"Successfully generated feed at: {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error writing feed file: {e}")
            
if __name__ == "__main__":
    generate_feed()