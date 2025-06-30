import feedparser

def fetch_and_parse_feeds(feed_urls):
    """Fetches and parses multiple RSS feeds."""
    all_content = []
    print("Fetching and parsing RSS feeds...")
    
    hf_papers = feedparser.parse(feed_urls['hf_papers']).entries
    pwc_papers = feedparser.parse(feed_urls['pwc_papers']).entries
    
    for i, paper in enumerate(hf_papers + pwc_papers):
        all_content.append({
            "index": i, "type": "paper", "title": paper.get('title', 'No Title'),
            "details": paper.get('summary', 'No Summary'), "link": paper.get('link', '')
        })
        
    git_repos = feedparser.parse(feed_urls['git_repos']).entries
    for i, repo in enumerate(git_repos):
        readme_content = repo.get('summary', 'No Summary')
        if 'content' in repo and repo.content:
            readme_content = repo.content[0].get('value', readme_content)
        all_content.append({
            "index": len(all_content), "type": "repo", "title": repo.get('title', 'No Title'),
            "details": readme_content, "link": repo.get('link', '')
        })
        
    if not all_content:
        print("No content found in feeds.")
    
    return all_content