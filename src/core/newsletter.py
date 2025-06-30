import json
from datetime import datetime
from src.utils import file_handler
import os 

class NewsletterGenerator:
    def __init__(self, gemini_service, cloudflare_service, prompts, output_paths, all_content):
        self.gemini = gemini_service
        self.cloudflare = cloudflare_service
        self.prompts = prompts
        self.output_paths = output_paths
        self.all_content = all_content
        self.today_date = datetime.now().strftime("%B %d, %Y")
        self.today_date_dir = datetime.now().strftime("%Y-%m-%d")
        
    def generate(self):
        """Orchestrates the newsletter generation process."""
        if not self.all_content:
            print("No content to process. Exiting newsletter generation.")
            return None

        themed_data = self._categorize_content()
        if not themed_data:
            return None

        theme_details = self._process_themes(themed_data)
        
        hero_image_path = self._generate_hero_image(theme_details)
        hero_image_path = os.path.join("..", "..", hero_image_path)
        
        introduction = self._generate_introduction(theme_details)
        
        newsletter_md = self._assemble_newsletter(theme_details, hero_image_path, introduction)
        
        newsletter_filename = f"newsletter_{self.today_date_dir}.md"
        newsletter_save_dir = os.path.join(self.output_paths['newsletters'], self.today_date_dir)
        file_handler.save_newsletter(newsletter_md, newsletter_save_dir, newsletter_filename)
        
        return newsletter_md

    def _call_gemini_with_prompt(self, prompt_name, **kwargs):
        """Helper to format and call the Gemini service with a specific prompt."""
        prompt_obj = self.prompts[prompt_name]
        formatted_prompt = prompt_obj.format(**kwargs)
        return self.gemini.generate_text(formatted_prompt, prompt_obj.system_prompt, prompt_obj.config["temperature"], prompt_obj.config["model"])

    def _categorize_content(self):
        print("Categorizing content into themes...")
        categorization_input = "\n".join(
            [f"Item {item['index']} ({item['type']}):\nTitle: {item['title']}\nSummary: {item['details'][:300]}...\n---" for item in self.all_content]
        )
        response = self._call_gemini_with_prompt('categorize', content=categorization_input)
        try:
            return json.loads(response)
        except (json.JSONDecodeError, TypeError):
            print(f"Error: Failed to decode JSON from categorization response.\nLLM Response:\n{response}")
            return None
        
    def _process_themes(self, themed_data):
        theme_details = {}
        print("Processing themes: generating summaries and images...")
        for theme_name, data in themed_data["themes"].items():
            items_in_theme = [c for c in self.all_content if c['index'] in data["items"]]
            
            summary = self._generate_theme_summary(theme_name, items_in_theme)
            header_image_path = self._generate_theme_image(theme_name, summary)
            header_image_path = os.path.join("..", "..", header_image_path)
            
            theme_details[theme_name] = {
                "summary": summary or "Summary could not be generated.",
                "items": items_in_theme,
                "header_image_path": header_image_path
            }
        return theme_details
    
    def _generate_theme_summary(self, theme_name, items):
        items_details_for_prompt = "\n\n".join([f"**Title: {item['title']}**\n**Details:**\n{item['details']}" for item in items])
        return self._call_gemini_with_prompt('analyst_journalist', theme_name=theme_name, items_details=items_details_for_prompt)
    
    def _generate_theme_image(self, theme_name, summary):
        prompt_json = self._call_gemini_with_prompt('art_director', theme_name=theme_name, theme_summary=summary)
        
        try:
            image_decision = json.loads(prompt_json)
            if "generation_prompt" in image_decision:
                generated_image_uri = self.cloudflare.generate_image(image_decision["generation_prompt"])
                image_save_dir = os.path.join(self.output_paths['images'], self.today_date_dir)
                return file_handler.save_image_from_data_uri(generated_image_uri, image_save_dir, theme_name.replace(" ", "_").lower())
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Could not parse image decision for theme '{theme_name}': {e}\nLLM Response: {prompt_json}")
        return "[https://placehold.co/1200x675/CCCCCC/FFFFFF?text=No+Image](https://placehold.co/1200x675/CCCCCC/FFFFFF?text=No+Image)"

    def _generate_hero_image(self, theme_details):
        print("Generating hero image...")
        themes_and_summaries = "\n\n".join([f"**{name}**:\n{details['summary']}" for name, details in theme_details.items()])
        hero_json = self._call_gemini_with_prompt('hero_image', themes_and_summaries=themes_and_summaries)

        try:
            hero_decision = json.loads(hero_json)
            if "generation_prompt" in hero_decision:
                hero_image_uri = self.cloudflare.generate_image(hero_decision["generation_prompt"])
                image_save_dir = os.path.join(self.output_paths['images'], self.today_date_dir)
                return file_handler.save_image_from_data_uri(hero_image_uri, image_save_dir, "hero_image")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Could not parse hero image decision: {e}\nLLM Response: {hero_json}")
        return "[https://placehold.co/1200x675/CCCCCC/FFFFFF?text=No+Image](https://placehold.co/1200x675/CCCCCC/FFFFFF?text=No+Image)"
    
    def _generate_introduction(self, theme_details):
        print("Generating introduction...")
        all_summaries = "\n\n".join([d['summary'] for d in theme_details.values()])
        return self._call_gemini_with_prompt('generate_intro', summaries=all_summaries)

    def _assemble_newsletter(self, theme_details, hero_image_path, introduction):
        print("Assembling final newsletter...")
        newsletter_md = f"# BYTE-SIZED AI & CODE - {self.today_date}\n\n"
        if hero_image_path:
            #newsletter_md += f"![Daily Byte Hero Image]({hero_image_path})\n\n"
            newsletter_md += "\\begin{center}\n"
            newsletter_md += f"\\includegraphics[width=0.5\\textwidth]{{{hero_image_path}}}\n"
            newsletter_md += "\\end{center}\n\n"
            #newsletter_md += f"<img src=\"{hero_image_path}\" alt=\"Daily Byte Hero Image\" style=\"width:50%; height:auto;\">\n\n"
        newsletter_md += "Your daily digest of trending AI research and developer tools.\n\n---\n\n"
        if introduction:
            newsletter_md += f"**Today's Overview:** {introduction}\n\n"

        for theme_name, details in theme_details.items():
            icon = "⚙️" if "GitHub" in theme_name else "🔬"
            #newsletter_md += f"![{theme_name}]({details['header_image_path']})\n\n"
            newsletter_md += "\\begin{center}\n"
            newsletter_md += f"\\includegraphics[width=0.5\\textwidth]{{{details['header_image_path']}}}\n"
            newsletter_md += "\\end{center}\n\n"
            #newsletter_md += f"<img src=\"{details['header_image_path']}\" alt=\"{theme_name}\" style=\"width:50%; height:auto;\">\n\n"
            newsletter_md += f"## {icon} {theme_name}\n\n"
            newsletter_md += f"{details['summary']}\n\n"
            newsletter_md += "**Key Links:**\n"
            for item in details['items']:
                newsletter_md += f"- [{item['title']}]({item['link']})\n"
            newsletter_md += "\n---\n\n"

        newsletter_md += "_Generated by The Daily Byte AI Assistant._\n"
        return newsletter_md