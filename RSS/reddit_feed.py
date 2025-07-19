import httpx
from feedgen.feed import FeedGenerator
from datetime import datetime
import os
from pathlib import Path
from urllib.parse import urljoin
import markdown2
import time


TODAY_STR = datetime.now().strftime('%Y-%m-%d')
OUTPUT_DIR = Path("/var/www/html")
BASE_URL = "https://www.reddit.com"

MAX_NUMBER_ANSWER_COMMENTS = 3


def generate_feed(subreddit_name):
    OUTPUT_PATH = OUTPUT_DIR / f"{subreddit_name}_top_posts.atom"
    subreddit_url = f"{BASE_URL}/r/{subreddit_name}/top.json?t=day&limit=5"
    try:
        response = httpx.get(subreddit_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            print("Rate limit exceeded, waiting for 60 seconds...")
            time.sleep(60)  
            response = httpx.get(subreddit_url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
        else:
            print(f"Error fetching subreddit: {e}")
            return

    print(f"Fetching subreddit: {subreddit_url}")
        
    data = response.json()
    print(f"Fetched {len(data['data']['children'])} posts from {subreddit_url}")

    fg = FeedGenerator()
    fg.title(f"Top posts of r/{subreddit_name} - {TODAY_STR}")
    fg.link(href=f"{BASE_URL}/r/{subreddit_name}/top?t=day")
    
    fg.id(f"{BASE_URL}/r/{subreddit_name}/top?t=day&limit=5")
    fg.subtitle(f"Daily top posts from r/{subreddit_name}")
    fg.language("en")
    
    for children in data['data']['children']:
        title = children['data']['title']
        print(f"Processing post: {title}")
        link_to_post = children['data']['permalink']
        link_outside = children['data']['url']
        selftext = children['data']["selftext"]
        topic = children['data'].get('link_flair_text', 'No Flair')
        upvote_ratio = children['data']['upvote_ratio']
        updoots = children['data']['ups']
        
        markdown_content = f"# {title}\n\n{selftext}\n{link_outside}\n\n**Topic:** {topic}\n**Upvote Ratio:** {upvote_ratio}\n**Upvotes:** {updoots}\n"
        markdown_content += f"[View on Reddit]({urljoin(BASE_URL, link_to_post)})\n"
        markdown_content += "## Comments:\n\n"
        
        #go to the post to get the comments
        post_url = urljoin(BASE_URL, link_to_post.rstrip('/') + ".json?sort=top&limit=5")
        try: 
            comments_response = httpx.get(post_url, headers={"User-Agent": "Mozilla/5.0"})
            comments_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                print("Rate limit exceeded, waiting for 60 seconds...")
                time.sleep(60)  
                comments_response = httpx.get(post_url, headers={"User-Agent": "Mozilla/5.0"})
                comments_response.raise_for_status()
            else:
                print(f"Error fetching comments: {e}")
                continue
        #the result is a list, the first element is the post, the second is the comments
        post_comments = comments_response.json()[1]['data']['children']
        print(f"Found {len(post_comments)} comments")
        for i, comment in enumerate(post_comments):
            if comment['kind'] == 'more' or comment['data']['author'] == "AutoModerator":
                continue
            message = comment['data']['body']
            message_score = comment['data']['score']
            link_to_comment_response = comment['data']['permalink']
            comment_response_url = urljoin(BASE_URL, link_to_comment_response.rstrip('/')+ ".json?sort=top&limit=5")
            print(comment_response_url)
            try :
                comment_responses = httpx.get(comment_response_url, headers={"User-Agent": "Mozilla/5.0"})
                comment_responses.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    print("Rate limit exceeded, waiting for 60 seconds...")
                    time.sleep(60)  
                    comment_responses = httpx.get(comment_response_url, headers={"User-Agent": "Mozilla/5.0"})
                    comment_responses.raise_for_status()
                else:
                    print(f"Error fetching comment responses: {e}")
                    continue
            comment_responses_data = comment_responses.json()[1]['data']["children"][0]['data']['replies']
            if isinstance(comment_responses_data, str):
                print(f"No responses found for comment {i+1}")
                comment_responses_data = []
            else:
                comment_responses_data = comment_responses_data["data"]["children"]
            print(f"Found {len(comment_responses_data)} responses to comment {i+1}")
            markdown_content += f"### Comment {i+1}:\n\n{message}\n\n**Score:** {message_score}\n"
            markdown_content += "#### Responses to this comment:\n\n"
            for j, answer in enumerate(comment_responses_data) : 
                if j > MAX_NUMBER_ANSWER_COMMENTS:
                    break
                if answer['kind'] == 'more':
                    continue
                try : 
                    response_comment = answer['data']['body']
                    response_upvotes = answer['data']['ups']
                    markdown_content += f"- {response_comment} (Upvotes: {response_upvotes})\n"
                except KeyError:
                    print(answer)
        fe = fg.add_entry()
        fe.title(title)
        fe.link(href=urljoin(BASE_URL, link_to_post))
        fe.id(urljoin(BASE_URL, link_to_post))
        fe.summary(markdown2.markdown(selftext + "\n" + link_outside))
        fe.content(markdown2.markdown(markdown_content), type='html')
        
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        fg.atom_file(str(OUTPUT_PATH), pretty=True)
        print(f"Successfully generated feed at: {OUTPUT_PATH}")
    except Exception as e:
        print(f"Error writing feed file: {e}")

if __name__ == "__main__":
    subreddits = [
    "MachineLearning",
    "machinelearningnews",
    "ArtificialInteligence",
    "technology",
    ]

    for subreddit in subreddits:
        generate_feed(subreddit)
