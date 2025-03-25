import os
import logging
import tempfile
from pathlib import Path
from slugify import slugify
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {str(e)}")
    raise


def generate_audio(text: str, title: str, output_dir: str) -> dict:
    """
    Generate audio from text using OpenAI's TTS API.

    Args:
        text (str): Text to convert to speech
        title (str): Title for the audio file
        output_dir (str): Directory to save the audio file

    Returns:
        dict: Dictionary containing audio file path and any notes
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate filename from title and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(
            c for c in title if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        filename = f"{safe_title}_{timestamp}.mp3"
        output_path = os.path.join(output_dir, filename)

        # Generate audio using OpenAI TTS
        response = client.audio.speech.create(
            model="tts-1", voice="alloy", input=text, speed=1.0
        )

        # Save the audio file
        response.stream_to_file(output_path)

        return {
            "audio_path": output_path,
            "note": "Audio generated successfully. You can play it below or download it.",
        }

    except Exception as e:
        logger.error(f"Error generating audio: {str(e)}")
        return {"error": f"Failed to generate audio: {str(e)}"}


def chunk_text_for_tts(text, max_chars=4000):
    """
    Split long text into chunks for TTS processing
    Deepgram has limits on text length for TTS
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    sentences = text.replace("\n", " ").split(". ")
    current_chunk = ""

    for sentence in sentences:
        # Add period back if it was removed during split
        if sentence and not sentence.endswith("."):
            sentence += "."

        # If adding this sentence would exceed the limit, save the chunk and start a new one
        if len(current_chunk) + len(sentence) + 1 > max_chars:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def generate_audio_from_long_text(text, title, output_dir="audio_files"):
    """Handle generating audio for longer texts by chunking"""
    if not text:
        return {"error": "No text provided for audio generation"}

    # Split text into manageable chunks
    chunks = chunk_text_for_tts(text)

    if len(chunks) == 1:
        # If only one chunk, use the regular function
        return generate_audio(text, title, output_dir)

    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Create a sanitized filename from the title
        safe_title = slugify(title[:50])
        filename = f"{safe_title}_{os.urandom(4).hex()}.mp3"
        filepath = os.path.join(output_dir, filename)

        # Process chunks and combine them
        with tempfile.TemporaryDirectory() as temp_dir:
            chunk_files = []

            # Generate audio for each chunk
            for i, chunk in enumerate(chunks):
                chunk_result = generate_audio(chunk, f"{title}_part_{i+1}", temp_dir)

                if "error" in chunk_result:
                    return chunk_result

                chunk_files.append(chunk_result["audio_path"])

            # In a real application, you would combine these audio files
            # For simplicity, we'll just return the first chunk for now
            # A complete solution would use a library like pydub to concatenate the files

            if chunk_files:
                # Copy the first file as a demonstration
                with open(chunk_files[0], "rb") as src, open(filepath, "wb") as dst:
                    dst.write(src.read())

                return {
                    "audio_path": filepath,
                    "filename": filename,
                    "note": "For long text, this is only a partial audio sample. A complete implementation would combine all audio chunks.",
                }
            else:
                return {"error": "Failed to generate any audio chunks"}

    except Exception as e:
        logger.error(f"Error generating audio from long text: {str(e)}")
        return {"error": f"Failed to generate audio: {str(e)}"}
