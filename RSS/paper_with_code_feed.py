import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import os
import re
import pytz

from pathlib import Path
from urllib.parse import urljoin

# Configuration
TODAY_STR = datetime.now().strftime('%Y-%m-%d')
TARGET_URL = f"https://paperswithcode.com/"
OUTPUT_DIR = Path("/var/www/html")  #nginx html directory on my raspberry pi
OUTPUT_FILENAME = "paper_with_code_trending.atom"
OUTPUT_PATH = OUTPUT_DIR / OUTPUT_FILENAME
BASE_URL = "https://paperswithcode.com/"
SELF_FEED_URL = "http://192.168.0.195/paper_with_code_trending.atom"

# Selectors main page
PAPER_SELECTOR = "div.paper-card"                                
TITLE_LINK_SELECTOR = "h1 > a[href^='/paper/']"                  
IMAGE_SELECTOR = "div.item-image" 
DATE_SELECTOR = "p.author-section span.item-date-pub"

# Selectors paper page
ABSTRACT_SELECTOR = "div.col-md-12 > p"

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
    fg.title(f"Papers With Code Trending - {TODAY_STR}")
    fg.link(href=TARGET_URL, rel='alternate')
    fg.id("https://paperswithcode.com/")
    fg.subtitle('Trending Machine Learning papers and code from Papers With Code, scraped feed.')
    fg.author({'name': "Unofficial Papers With Code Feed"})
    fg.language('en')
    fg.load_extension('media')
    fg.link(href=SELF_FEED_URL, rel='self')

    paper_elements = soup.select(PAPER_SELECTOR)
    print(f"Found {len(paper_elements)} paper elements using selector '{PAPER_SELECTOR}'.")

    for paper_elem in paper_elements:
        #print(f"Processing paper element: {paper_elem}")
        title_link_elem = paper_elem.select_one(TITLE_LINK_SELECTOR)
        image_elem = paper_elem.select_one(IMAGE_SELECTOR)
        date_elem = paper_elem.select_one(DATE_SELECTOR)
        
        if title_link_elem:
            title = title_link_elem.get_text(strip=True)
            paper_url = urljoin(BASE_URL, title_link_elem['href'])
            entry = fg.add_entry()
            entry.title(title)
            entry.link(href=paper_url, rel='alternate')
            entry.id(paper_url)
            
            # add date
            if date_elem:
                date_str = date_elem.get_text(strip=True)

                published_date = datetime.strptime(date_str, '%d %b %Y')
                published_date = pytz.utc.localize(published_date)
                entry.pubDate(published_date)
            try :
                paper_response = requests.get(paper_url, headers=headers, timeout=30)
                paper_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching paper URL: {e}")
                continue
            paper_soup = BeautifulSoup(paper_response.content, 'lxml')
            abstract_elem = paper_soup.select_one(ABSTRACT_SELECTOR)
            
            # add abstract
            if abstract_elem:
                entry.summary(abstract_elem.get_text(strip=True))
                
            # add image
            if image_elem and 'background-image' in image_elem['style']:
                style = image_elem['style']
                if "https://" in style:
                    regex = r"https://[^'\s]+"
                    match_https = re.search(regex, style)
                    if match_https:
                        image_url = match_https.group(0)
                        mime_type = 'image/jpeg'
                        medium = "image"
                elif "data:image" in style:
                    regex_data = r"data:image/(?P<mime>[a-z]+);base64,(?P<data>.+)"
                    match_data = re.search(regex_data, style)
                    if match_data:
                        mime_type = f"image/{match_data.group('mime')}"
                        image_url = match_data.group('data')
                        medium = "image"
                entry.media.content(url=image_url, type=mime_type, medium=medium)
            
        else:
            print("Warning: Could not find title/link using selector.")
            continue

    fg.atom_file(str(OUTPUT_PATH), pretty=True)
    print(f"Feed generated successfully at: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_feed()