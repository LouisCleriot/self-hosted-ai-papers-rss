import yaml
import os
from dotenv import load_dotenv
from src.services.gemini_service import GeminiService
from src.services.cloudflare_service import CloudflareService
from src.utils.rss_parser import fetch_and_parse_feeds
from src.utils.prompt_parser import load_prompts
from src.core.newsletter import NewsletterGenerator
from src.core.podcast import PodcastGenerator

def load_config():
    """Loads main configuration from YAML file."""
    with open("config/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config

def main(generate_podcast=False):
    """Main function to run the newsletter and podcast generation."""
    load_dotenv()
    
    config = load_config()
    prompts = load_prompts()
    
    # Initialize services
    gemini_service = GeminiService(
        api_key=config['api_keys']['google_api_key'],
        audio_model_config=config['models']['audio_model']
    )
    cloudflare_service = CloudflareService(
        account_id=config['api_keys']['cloudflare_account_id'],
        api_token=config['api_keys']['cloudflare_api_token'],
        model_name=config['models']['image_model']['name']
    )

    all_content = fetch_and_parse_feeds(config['rss_feeds'])

    newsletter_generator = NewsletterGenerator(
        gemini_service, 
        cloudflare_service, 
        prompts, 
        config['output_paths'],
        all_content
    )
    newsletter_content = newsletter_generator.generate()
    
    if generate_podcast:
        podcast_generator = PodcastGenerator(
            gemini_service,
            prompts,
            config['output_paths'],
        )
        podcast_generator.generate(newsletter_content)

if __name__ == "__main__":
    main()