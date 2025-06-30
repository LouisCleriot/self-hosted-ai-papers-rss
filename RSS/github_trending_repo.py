import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import os
from pathlib import Path
from urllib.parse import urljoin
import markdown2

TODAY_STR = datetime.now().strftime('%Y-%m-%d')
TARGET_URL = "https://github.com/trending"
OUTPUT_DIR = Path("/var/www/html")
OUTPUT_FILENAME = "github_trending_repos.atom"
OUTPUT_PATH = OUTPUT_DIR / OUTPUT_FILENAME
BASE_URL = "https://github.com"
SELF_FEED_URL = "http://192.168.0.195/github_trending_repos.atom"

REPO_SELECTOR = "article.Box-row"
TITLE_LINK_SELECTOR = "h2.h3 > a"
DESCRIPTION_SELECTOR = "p.col-9.color-fg-muted"
STARS_TODAY_SELECTOR = "span.d-inline-block.float-sm-right"

def get_and_process_readme(repo_url):
    """
    Fetches the README for a repo, converts it to HTML, and fixes relative paths.
    """
    try:
        readme_url = repo_url.replace('github.com', 'raw.githubusercontent.com') + '/refs/heads/main/README.md'
        branch="main"
        headers = {'User-Agent': 'Your-RSS-Generator/1.0'}
        response = requests.get(readme_url, headers=headers, timeout=15)
        if response.status_code != 200:
            readme_url = repo_url.replace('github.com', 'raw.githubusercontent.com') + '/refs/heads/master/README.md'
            response = requests.get(readme_url, headers=headers, timeout=15)
            branch = "master"

        response.raise_for_status() 
        
        html_content = markdown2.markdown(response.text, extras=["tables", "fenced-code-blocks", "strike"])
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        repo_content_base_url = repo_url + '/blob/' + branch + '/'

        for tag in soup.find_all(['a', 'img']):
            if tag.name == 'a' and 'href' in tag.attrs and not tag['href'].startswith(('http', '#')):
                tag['href'] = urljoin(repo_content_base_url, tag['href'])
            if tag.name == 'img' and 'src' in tag.attrs and not tag['src'].startswith('http'):
                raw_image_base = repo_url.replace('github.com', 'raw.githubusercontent.com') + '/' + branch + '/'
                tag['src'] = urljoin(raw_image_base, tag['src'])
                
        return str(soup)

    except requests.exceptions.RequestException as e:
        print(f"Could not fetch or find README for {repo_url}: {e}")
        return None

def generate_feed():
    """Fetches trending repositories from GitHub and generates an RSS feed."""
    print(f"Fetching repositories from: {TARGET_URL}")

    headers = {
        'User-Agent': 'Your-RSS-Generator/1.0 (python-requests; +http://github.com)'
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return

    soup = BeautifulSoup(response.content, 'lxml')

    # --- Feed Initialization ---
    fg = FeedGenerator()
    fg.title(f"GitHub Trending Repositories - {TODAY_STR}")
    fg.link(href=TARGET_URL, rel='alternate')
    fg.id(TARGET_URL)
    fg.subtitle('Daily digest of trending repositories from GitHub.')
    fg.author({'name': "Unofficial GitHub Trending Feed"})
    fg.language('en')
    fg.link(href=SELF_FEED_URL, rel='self')

    repo_elements = soup.select(REPO_SELECTOR)
    print(f"Found {len(repo_elements)} repository elements using selector '{REPO_SELECTOR}'.")

    for repo_elem in repo_elements:
        title_link_elem = repo_elem.select_one(TITLE_LINK_SELECTOR)

        if not title_link_elem:
            print(f"Warning: Could not find title/link using '{TITLE_LINK_SELECTOR}'")
            continue

        repo_name = title_link_elem.get_text(strip=True).replace("\n", "").replace(" ", "")
        relative_repo_url = title_link_elem['href']
        absolute_repo_url = urljoin(BASE_URL, relative_repo_url)

        if not repo_name or not absolute_repo_url:
            print("Warning: Missing repository name or URL. Skipping.")
            continue

        fe = fg.add_entry()
        fe.title(repo_name)
        fe.link(href=absolute_repo_url)
        fe.id(absolute_repo_url)

        description_elem = repo_elem.select_one(DESCRIPTION_SELECTOR)
        description = description_elem.get_text(strip=True) if description_elem else "No description provided."

        stars_today_elem = repo_elem.select_one(STARS_TODAY_SELECTOR)
        stars_today = "Not available"
        if stars_today_elem:
            stars_today = stars_today_elem.get_text(strip=True)
        
        # --- Constructing the content for the feed entry ---
        #content_html = f"{description}"
        final_content = f"Stars today: {stars_today.replace('stars today', '').strip()}"
        
        fe.summary(description)
        
        readme_html = get_and_process_readme(absolute_repo_url)
        
        if readme_html:
            final_content += readme_html
        else:
            # Fallback content if README is not found
            final_content += "<p><i>README not found or could not be processed.</i></p>"

        
        fe.content(final_content, type='html')

    # --- Saving the Feed ---
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        fg.atom_file(str(OUTPUT_PATH), pretty=True)
        print(f"Successfully generated feed at: {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error writing feed file: {e}")

if __name__ == "__main__":
    generate_feed()