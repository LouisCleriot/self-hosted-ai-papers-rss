import yaml
import os
import re

class Prompt:
    """A class to hold a parsed prompt's configuration and template."""
    def __init__(self, config, system_prompt, user_prompt):
        self.config = config
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    def format(self, **kwargs):
        """Formats the user_prompt with the given arguments."""
        return self.user_prompt.format(**kwargs)

def parse_prompt_file(file_path):
    """
    Parses a .prompt file into its YAML frontmatter (config) and body (template).
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Regex to split the YAML frontmatter from the rest of the content
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        raise ValueError(f"Prompt file '{file_path}' is not formatted correctly.")

    yaml_header, template_body = match.groups()
    config = yaml.safe_load(yaml_header)

    system_prompt = re.search(r'<system>(.*?)</system>', template_body, re.DOTALL)
    user_prompt = re.search(r'<user>(.*?)</user>', template_body, re.DOTALL)

    if not system_prompt or not user_prompt:
        raise ValueError(f"Prompt file '{file_path}' is not formatted correctly.")

    return Prompt(config, system_prompt.group(1).strip(), user_prompt.group(1).strip())

def load_prompts(directory="prompts"):
    """Loads all .prompt files from a directory into a dictionary."""
    prompts = {}
    for filename in os.listdir(directory):
        if filename.endswith(".prompt"):
            prompt_name = filename.replace(".prompt", "")
            file_path = os.path.join(directory, filename)
            prompts[prompt_name] = parse_prompt_file(file_path)
            print(f"Loaded prompt: {prompt_name}")
    return prompts