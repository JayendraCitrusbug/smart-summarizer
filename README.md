# Smart Content Summary & Audio Generator

A Streamlit-based Python application that extracts content from YouTube videos and articles, generates AI-powered summaries, and converts them to audio. The application uses OpenAI for summarization and text-to-speech conversion.

## Features

- **Content Extraction**:

  - YouTube video content and transcripts
  - Article/blog content
  - Automatic metadata extraction (title, publish date)

- **AI-Powered Summarization**:

  - Multiple summary styles:
    - Quick Takeaways
    - Deep Dive
    - Key Quotes
    - Key Principles/Lessons
  - Context-aware summaries
  - Optimized for audio conversion

- **Audio Generation**:
  - Text-to-speech conversion
  - Audio file management
  - Automatic cleanup of old audio files
  - Download functionality

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection for content extraction

## Installation

1. Clone the repository:

```bash
git clone git@github.com:JayendraCitrusbug/smart-summarizer.git
cd smart-summarizer
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

## Project Structure

```
smart-summarizer/
├── app.py                 # Main Streamlit application
├── content_extractor.py   # Content extraction from URLs
├── summarizer.py         # AI-powered content summarization
├── audio_generator.py    # Text-to-speech conversion
├── requirements.txt      # Project dependencies
├── .env                 # Environment variables
└── audio_files/         # Generated audio files
```

## Dependencies

- `streamlit`: Web application framework
- `openai`: OpenAI API client
- `python-dotenv`: Environment variable management
- `pathlib`: File system operations

## Usage

1. Start the application:

```bash
streamlit run app.py
```

2. Enter a YouTube URL or article/blog link

3. Select a summary style:

   - Quick Takeaways: Concise bullet points
   - Deep Dive: Comprehensive analysis
   - Key Quotes: Important excerpts
   - Key Principles/Lessons: Main takeaways

4. Click "Generate Summary" to:
   - Extract content
   - Generate AI summary
   - Create audio version
   - Display results

## Features in Detail

### Content Extraction

- Supports YouTube videos and articles
- Extracts title, content, and publish date
- Handles various URL formats
- Error handling for invalid URLs

### Summarization

- Context-aware summaries
- Multiple summary styles
- Optimized for audio conversion
- Error handling for API issues

### Audio Generation

- Text-to-speech conversion
- Automatic file management
- 3-minute file retention
- Download functionality

## Error Handling

The application includes comprehensive error handling for:

- Invalid URLs
- Content extraction failures
- API errors
- File system operations
- Audio generation issues
