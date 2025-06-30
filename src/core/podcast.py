import os
from datetime import datetime
from src.utils import file_handler

class PodcastGenerator:
    def __init__(self, gemini_service, prompts, output_paths):
        self.gemini = gemini_service
        self.prompts = prompts
        self.output_paths = output_paths
        self.today_date_dir = datetime.now().strftime("%Y-%m-%d")

    def generate(self, newsletter_content):
        """Generates a podcast from the newsletter content."""
        if not newsletter_content:
            print("No newsletter content available for podcast generation.")
            return

        print("\n--- Starting Podcast Generation ---")
        podcast_script = self._generate_script(newsletter_content)

        if podcast_script:
            podcast_audio_data = self.gemini.generate_audio(podcast_script)
            podcast_save_dir = os.path.join(self.output_paths['podcasts'], self.today_date_dir)
            file_handler.save_audio_file(podcast_audio_data, podcast_save_dir)
        else:
            print("Could not generate podcast script. Skipping audio generation.")

    def _generate_script(self, newsletter_content):
        promptobj = self.prompts['generate_podcast_script']
        formated_prompt = promptobj.format(newsletter_content=newsletter_content)
        return self.gemini.generate_text(
            formated_prompt,
            promptobj.system_prompt,
            promptobj.config["temperature"],
            promptobj.config["model"]
        )