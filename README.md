# AI-Powered Newsletter and Podcast Generator

This project automates the creation of a daily newsletter and an accompanying podcast summarizing the latest news in the world of Artificial Intelligence. It's a two-part system: first, it scrapes various sources to generate custom RSS feeds, and second, it consumes these feeds to produce a newsletter and podcast.

## How it Works

The project operates in two main stages:

1. **RSS Feed Generation**: Python scripts in the `RSS` directory scrape trending data from GitHub, Hugging Face, and Papers with Code. These scripts generate custom Atom XML feeds, which are then served locally.
2. **Newsletter and Podcast Generation**: The main Python script (`main.py`) fetches and parses the articles from the generated RSS feeds. It then uses the Gemini API for content categorization and text generation, and the Cloudflare API for image generation, to create a daily newsletter in Markdown format. The script can also generate a podcast from the newsletter content.

## Features

- **Self-Hosted RSS Feeds**: Generates custom RSS feeds for Hugging Face, Papers With Code, and GitHub trending repositories.
- **RSS Feed Aggregation**: Fetches and parses articles from multiple RSS feeds.
- **AI-Powered Content Categorization**: Uses the Gemini API to categorize articles into relevant topics.
- **Newsletter Generation**: Creates a daily newsletter in Markdown format, including a hero image and images for each article.
- **Podcast Generation**: Generates a podcast script and audio from the newsletter content.
- **Image Generation**: Uses the Cloudflare API to generate images for the newsletter.
- **Extensible**: The project is designed to be easily extensible with new RSS feeds, prompts, and output formats.

## Getting Started

### Prerequisites

- A Linux-based system (e.g., Raspberry Pi) for the RSS feed generation
- Python 3.11
- Pip
- A virtual environment (recommended)
- API keys for Google Gemini and Cloudflare
- A web server (like Nginx) to host the generated RSS feeds

### Installation

1. **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository.git](https://github.com/your-username/your-repository.git)
    cd your-repository
    ```
2. **Set up the RSS Feed Generation:**
    - Navigate to the `RSS` directory: `cd RSS`
    - Create and activate a virtual environment:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    - Install the required dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    - Set up a web server (like Nginx) to serve the generated Atom files from the `/var/www/html` directory.
    - Make the update script executable:
        ```bash
        sudo chmod u+x update_feed.sh
        ```
3. **Set up the Newsletter and Podcast Generation:**
    - Navigate to the root directory.
    - Create and activate a virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate
        ```
    - Install the required dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    - Create a `.env` file in the root of the project and add your API keys:
        ```
        GOOGLE_API_KEY="your_google_api_key"
        CLOUDFLARE_ACCOUNT_ID="your_cloudflare_account_id"
        CLOUDFLARE_API_TOKEN="your_cloudflare_api_token"
        ```
4. **Configure the application:**
    - Open the `config/config.yaml` file to customize the RSS feeds, models, and output paths.

## Usage

1. **Generate the RSS Feeds:**
    - From the `RSS` directory, run the `update_feed.sh` script. This will generate the Atom feed files. You can set this up as a cron job to run periodically.
2. **Generate the Newsletter and Podcast:**
    - From the root directory, run the `generate_news.sh` script:
        ```bash
        ./generate_news.sh
        ```
    - This script will run the main Python script to generate the newsletter and podcast, and then convert the newsletter from Markdown to PDF.

## Project Structure
```
├── RSS/
│   ├── github_trending_repo.py
│   ├── hf_papers_feed.py
│   ├── paper_with_code_feed.py
│   ├── readme.md
│   ├── requirements.txt
│   └── update_feed.sh
├── config/
│   └── config.yaml
├── prompts/
│   ├── ...
├── src/
│   ├── core/
│   │   ├── newsletter.py
│   │   └── podcast.py
│   ├── services/
│   │   ├── cloudflare_service.py
│   │   └── gemini_service.py
│   └── utils/
│       ├── file_handler.py
│       ├── prompt_parser.py
│       └── rss_parser.py
├── main.py
├── requirements.txt
└── generate_news.sh
```
- **`RSS/`**: Contains the scripts for generating the self-hosted RSS feeds.
- **`config/`**: Contains the main configuration file for the project.
- **`prompts/`**: Stores the prompts used to interact with the language model.
- **`src/`**: The main source code for the newsletter and podcast generation.
  - **`core/`**: The core logic for generating the newsletter and podcast.
  - **`services/`**: Services for interacting with external APIs (Gemini, Cloudflare).
  - **`utils/`**: Utility functions for file handling, prompt parsing, and RSS parsing.
- **`main.py`**: The main entry point for the newsletter and podcast generation.
- **`requirements.txt`**: A list of the Python dependencies for the project.
- **`generate_news.sh`**: A shell script to automate the newsletter and podcast generation process.

## Technologies Used

- **Python**: The primary programming language for the project.
- **Google Gemini**: Used for content categorization, text generation, and audio generation.
- **Cloudflare Workers AI**: Used for image generation.
- **`feedparser`**: For parsing RSS feeds.
- **`requests`**: For making HTTP requests.
- **`BeautifulSoup`**: For scraping websites and cleaning up HTML content from RSS feeds.
- **`feedgen`**: For generating the Atom feeds.
- **`pandoc`**: For converting the newsletter from Markdown to PDF.