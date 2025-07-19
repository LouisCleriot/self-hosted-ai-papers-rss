import feedparser

def fetch_and_parse_feeds(feed_urls):
    """Fetches and parses multiple RSS feeds."""
    papers_content = []
    reddit_content = []
    repos_content = []
    print("Fetching and parsing RSS feeds...")
    
    hf_papers = feedparser.parse(feed_urls['hf_papers']).entries
    pwc_papers = feedparser.parse(feed_urls['pwc_papers']).entries
    index = 0
    for i, paper in enumerate(hf_papers + pwc_papers):
        papers_content.append({
            "index": index, "type": "paper", "title": paper.get('title', 'No Title'),
            "details": paper.get('summary', 'No Summary'), "link": paper.get('link', '')
        })
        index += 1

    git_repos = feedparser.parse(feed_urls['git_repos']).entries
    index = 0
    for repo in git_repos:
        readme_content = repo.get('summary', 'No Summary')
        if 'content' in repo and repo.content:
            readme_content = repo.content[0].get('value', readme_content)
        repos_content.append({
            "index": index, "type": "repo", "title": repo.get('title', 'No Title'),
            "details": readme_content, "link": repo.get('link', '')
        })
        index += 1

    reddit_feeds = [
        feedparser.parse(feed_urls['artificial_intelligence_reddit']).entries,
        feedparser.parse(feed_urls['machine_learning_reddit']).entries,
        feedparser.parse(feed_urls['machine_learning_news_reddit']).entries,
        feedparser.parse(feed_urls['technology_reddit']).entries
    ]
    index = 0
    for feed in reddit_feeds:
        for post in feed:
            reddit_content.append({
                "index": index, "type": "reddit_post", "title": post.get('title', 'No Title'),
                "details": post.get('content', 'No Content'), "link": post.get('id', '')
            })
            index += 1
    
    return papers_content, reddit_content, repos_content