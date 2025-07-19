#!/bin/bash

cd "$(dirname "$0")"

source ./venv/bin/activate

python3 hf_papers_feed.py
python3 paper_with_code_feed.py
python3 github_trending_repo.py
python3 reddit_feed.py
