# Smart Content Summary & Audio Generator

A Streamlit-based Python application that extracts content from YouTube videos and articles, generates AI-powered summaries, and converts them to audio using OpenAI's TTS.

## Features

- **Content Extraction**:

  - YouTube video content extraction
  - Article/blog content extraction
  - Automatic metadata detection (title, publish date)

- **AI Summarization**:

  - Multiple summary styles:
    - Quick Takeaways
    - Deep Dive
    - Key Quotes
    - Key Principles/Lessons
  - Powered by OpenAI's GPT models

- **Audio Generation**:
  - Text-to-speech conversion using OpenAI's TTS
  - High-quality voice synthesis
  - Automatic audio file management
  - Support for long-form content through text chunking

## Prerequisites

- Python 3.10 or higher
- OpenAI API key
- YouTube Data API key (for YouTube content extraction)

## Installation

1. Clone the repository:

```bash
git clone git@github.com:JayendraCitrusbug/smart-summarizer.git
cd smart-summarizer
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file in the project root with:

```
OPENAI_API_KEY=your_openai_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

## Project Structure

```
smart-summarizer/
├── app.py                 # Main Streamlit application
├── content_extractor.py   # Content extraction from URLs
├── summarizer.py         # AI-powered text summarization
├── audio_generator.py    # Text-to-speech conversion
├── requirements.txt      # Project dependencies
├── .env                 # Environment variables
└── audio_files/         # Generated audio files
```

## Usage

1. Run the application:

```bash
streamlit run app.py
```

2. Enter a YouTube URL or article/blog link

3. Select your preferred summary style:

   - Quick Takeaways: Concise bullet points
   - Deep Dive: Comprehensive analysis
   - Key Quotes: Important excerpts
   - Key Principles/Lessons: Main takeaways

4. Click "Generate Summary" to get the AI summary

5. (Optional) Click "Create Audio Version" to generate an audio version of the summary

## Dependencies

- streamlit: Web application framework
- openai: OpenAI API client
- python-dotenv: Environment variable management
- python-slugify: URL-friendly text conversion

## Notes

- The application requires valid API keys for OpenAI and YouTube Data API
- Audio generation supports long-form content through automatic text chunking
- Generated audio files are saved in the `audio_files` directory
- The application uses OpenAI's latest TTS model (tts-1) for high-quality voice synthesis
