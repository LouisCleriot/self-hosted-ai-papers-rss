from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

class GeminiService:
    def __init__(self, api_key, audio_model_config):
        #genai.configure(api_key=api_key)
        self.audio_model_name = audio_model_config['name']
        self.audio_config = self._create_audio_config(audio_model_config)
        self.client = genai.Client(api_key=api_key)

    def _create_audio_config(self, config):
        """Creates the multi-speaker audio configuration."""
        speaker_configs = [
            types.SpeakerVoiceConfig(
                speaker=speaker,
                voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=details['voice_name']))
            )
            for speaker, details in config['multi_speaker_voice_config']['speakers'].items()
        ]
        return types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(speaker_voice_configs=speaker_configs)
            )
        )
    
    def generate_text(self, prompt_content, system_prompt, temperature, model_name):
        """
        Sends a prompt to the Gemini API for text generation.
        """
        print("Calling Gemini API for text generation...")        

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_prompt
        )
        try:
            response = self.client.models.generate_content(
                model=model_name,
                config=config,
                contents=prompt_content
            )
            text_response = response.text.strip()
            if text_response.startswith("```json"):
                text_response = text_response[7:-3].strip()
            elif text_response.startswith("`"):
                text_response = text_response.strip("`")
            return text_response
        except Exception as e:
            print(f"An error occurred during the Gemini text API call: {e}")
            return None
        
    def generate_audio(self, script):
        """Generates multi-speaker audio from a script using Gemini TTS."""
        print("Generating podcast audio with Gemini TTS...")
        try:
            tts_prompt = f"TTS the following podcast conversation:\n\n{script}"
            response = self.client.models.generate_content(
                model=self.audio_model_name,
                contents=tts_prompt,
                config=self.audio_config
            )
            return response.candidates[0].content.parts[0].inline_data.data
        except Exception as e:
            print(f"An error occurred during the Gemini TTS API call: {e}")
            return None