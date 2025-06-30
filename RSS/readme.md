# Self-Hosted RSS Feed for Hugging Face and Papers With Code

This project provides a self-hosted RSS feed for trending AI papers from Hugging Face and Papers With Code. It uses Python scripts to scrape the websites, parse the information with BeautifulSoup, and generate Atom feed files using FeedGenerator. These feeds can then be accessed via a web server like Nginx.

## Files Included

* **`hf_papers_feed.py`**: Python script to scrape daily AI papers from Hugging Face and generate an Atom feed.
* **`paper_with_code_feed.py`**: Python script to scrape trending machine learning papers and code from Papers With Code and generate an Atom feed.
* **`requirements.txt`**: Lists the Python dependencies required for the scripts.
* **`readme.md`**: This file, providing instructions and information about the project.
* **`update_feed.sh`**: Shell script to activate the virtual environment and run the Python scripts to update the feeds.

## Setup Instructions

### Prerequisites

* A Linux-based system (e.g., Raspberry Pi)
* Python 3
* `pip` package installer

### Installation

1.  **Clone or download this project repository.**
2.  **Navigate to the project directory:**
    ```bash
    cd temp
    ```
3.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    ```
4.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```
5.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install the necessary libraries: `requests`, `beautifulsoup4`, `feedgen`, and `pytz`.

### Web Server Setup (Nginx Example)

This guide assumes you are using Nginx as your web server.

1.  **Install Nginx:**
    ```bash
    sudo apt update
    sudo apt install nginx
    ```
2.  **Grant write access to the web directory:** This allows the Python scripts to save the generated feed files.
    ```bash
    sudo chown -R $USER:$USER /var/www/html
    ```
    Replace `$USER` with your username.

### Running the Feed Generation

1.  **Make the `update_feed.sh` script executable:**
    ```bash
    sudo chmod u+x update_feed.sh
    ```
2.  **Run the script to generate the feeds:**
    ```bash
    ./update_feed.sh
    ```
    This script will execute both `hf_papers_feed.py` and `paper_with_code_feed.py`, creating the Atom feed files in the `/var/www/html` directory.
    * `huggingface_daily_papers.atom`
    * `paper_with_code_trending.atom`

### Scheduling Automatic Updates (Cron Job)

To automatically update the feeds at a regular interval, you can add a cron job. This example schedules the update to run daily at 3:00 AM.

1.  **Open the crontab editor:**
    ```bash
    crontab -e
    ```
2.  **Add the following line to the crontab file:**
    ```
    0 3 * * * /path/to/your/project/temp/update_feed.sh
    ```
    Replace `/path/to/your/project/temp/` with the actual path to the `update_feed.sh` script.

## Accessing the Feeds

Once the feeds are generated and the web server is configured, you can access them through your web browser or an RSS reader using the following URLs (replace `192.168.0.195` with the actual IP address or domain name of your server):

* **Hugging Face Daily Papers:** `http://192.168.0.195/huggingface_daily_papers.atom`
* **Papers With Code Trending:** `http://192.168.0.195/paper_with_code_trending.atom`

## Customization

You can customize the behavior of the scripts by modifying the following variables within each Python file:

* **`TARGET_URL`**: The URL of the page to scrape.
* **`OUTPUT_DIR`**: The directory where the Atom feed file will be saved (currently set to `/var/www/html`).
* **`OUTPUT_FILENAME`**: The name of the generated Atom feed file.
* **`BASE_URL`**: The base URL of the website being scraped.
* **`SELF_FEED_URL`**: The URL where the generated feed will be accessible.
* **Selectors**: The CSS selectors used to locate specific elements on the web pages (e.g., paper titles, links, abstracts). You may need to adjust these if the website structure changes.

This project provides a convenient way to stay updated on the latest AI research from Hugging Face and Papers With Code by hosting your own RSS feed.