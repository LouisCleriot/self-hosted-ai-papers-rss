#!/bin/bash

cd "$(dirname "$0")"

source ./venv/bin/activate

sudo python3 hf_papers_feed.py
sudo python3 paper_with_code_feed.py