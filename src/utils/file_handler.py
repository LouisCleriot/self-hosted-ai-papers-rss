import os
import base64
import wave
from datetime import datetime
import contextlib

def save_image_from_data_uri(image_data_uri, save_dir, file_name):
    """Saves a base64 data URI image and returns its local path."""
    if not image_data_uri:
        return "[Image generation failed](https://placehold.co/1200x675/FF0000/FFFFFF?text=Generation+Failed)"
    try:
        image_data = image_data_uri.split(",")[1]
        image_bytes = base64.b64decode(image_data)
        safe_file_name = "".join(c for c in file_name if c.isalnum() or c in (' ', '_')).rstrip()
        image_filename = os.path.join(save_dir, f"{safe_file_name}.jpeg")
        
        os.makedirs(os.path.dirname(image_filename), exist_ok=True)
        with open(image_filename, "wb") as img_file:
            img_file.write(image_bytes)
        return image_filename
    except Exception as e:
        print(f"Failed to save image {file_name}: {e}")
        return "[Image saving failed](https://placehold.co/1200x675/FF0000/FFFFFF?text=Save+Failed)"
    
@contextlib.contextmanager
def wave_file(filename, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        yield wf

def save_audio_file(audio_data, save_dir, file_name="newsletter_podcast.wav"):
    """Saves binary audio data to a WAV file."""
    if not audio_data:
        print("No audio data to save.")
        return None
    try:
        audio_filename = os.path.join(save_dir, file_name)
        os.makedirs(os.path.dirname(audio_filename), exist_ok=True)
        with wave_file(audio_filename) as wf:
            wf.writeframes(audio_data)
        print(f"--- Podcast saved successfully to {audio_filename} ---")
        
    except Exception as e:
        print(f"Failed to save audio file: {e}")
        return None

def save_newsletter(content, save_dir, filename):
    """Saves the newsletter content to a Markdown file."""
    os.makedirs(save_dir, exist_ok=True)
    output_path = os.path.join(save_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"--- Newsletter generation complete! Saved to {output_path} ---")