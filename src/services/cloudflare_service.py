import requests

class CloudflareService:
    def __init__(self, account_id, api_token, model_name):
        self.account_id = account_id
        self.api_token = api_token
        self.api_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{model_name}"

    def generate_image(self, prompt):
        """Generates an image using Cloudflare Workers AI and returns a base64 data URI."""
        print(f"Generating image with prompt: '{prompt}'")
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"prompt": prompt}
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            json_response = response.json()
            base64_image = json_response['result']['image']
            return f"data:image/jpeg;base64,{base64_image}"
        except requests.RequestException as e:
            print(f"Error generating image with Cloudflare: {e}")
            return None