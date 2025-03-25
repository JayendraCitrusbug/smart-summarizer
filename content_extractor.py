import datetime
import os
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_youtube_url(url):
    """Check if the URL is a YouTube URL"""
    youtube_regex = (
        r"(https?://)?(www\.)?"
        r"(youtube|youtu|youtube-nocookie)\.(com|be)/"
        r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
    )

    match = re.match(youtube_regex, url)
    return bool(match)


def extract_youtube_id(url):
    """Extract the YouTube video ID from a URL"""
    if "youtu.be" in url:
        return url.split("/")[-1]

    video_id = None
    parsed_url = urlparse(url)
    if "youtube.com" in parsed_url.netloc:
        if "v=" in parsed_url.query:
            query_params = parsed_url.query.split("&")
            for param in query_params:
                if param.startswith("v="):
                    video_id = param[2:]
                    break
    return video_id


def get_published_date(video_id, api_key):
    """
    Fetches the published date of a YouTube video using the YouTube Data API v3.
    :param video_id: Video Id
    :param api_key: Your Google API Key
    :return: Published date if available
    """
    # Step 1: Get video details (including published date)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={api_key}"
    video_response = requests.get(url)
    video_data = video_response.json()

    if "items" not in video_data or not video_data["items"]:
        return {"error": "Video not found."}

    try:
        published_date = video_data["items"][0]["snippet"]["publishedAt"]
        published_date = datetime.datetime.strptime(
            published_date, "%Y-%m-%dT%H:%M:%SZ"
        )

        return {"published_date": published_date.strftime("%Y-%m-%d")}
    except Exception as e:
        return {"error": "Error parsing published date."}


def get_youtube_content(url):
    """Extract transcript and metadata from a YouTube video"""
    video_id = extract_youtube_id(url)
    if not video_id:
        return {"error": "Could not extract YouTube video ID"}

    try:
        # Get published date
        published_date_data = get_published_date(
            video_id, os.getenv("YOU_TUBE_API_KEY")
        )
        if "error" in published_date_data:
            published_date = "Date not available."
        else:
            published_date = published_date_data["published_date"]

        # Get the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry["text"] for entry in transcript_list])

        # Get video title and publish date (this is simplified - in a real app, you'd use the YouTube API)
        # For now, we'll scrape it from the page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("meta", property="og:title")
        title = title["content"] if title else "Unknown Title"

        return {
            "title": title,
            "publish_date": published_date,
            "content": transcript_text,
            "source_type": "youtube",
        }
    except TranscriptsDisabled:
        return {"error": "Transcripts are disabled for this video"}
    except Exception as e:
        logger.error(f"Error extracting YouTube content: {str(e)}")

        if "Could not retrieve a transcript for the video" in str(e):
            return {"error": "Transcripts are disabled for this video"}

        return {"error": f"Failed to extract content: {str(e)}"}


def get_article_content(url):
    """Extract main content from an article or blog post"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = soup.find("title")
        title = title.text if title else "Unknown Title"

        # Try to find publish date (this is a simplification)
        publish_date = "Date not available"
        date_meta_tags = soup.select(
            'meta[property="article:published_time"], meta[name="pubdate"], meta[name="publishdate"], meta[name="date"]'
        )

        if date_meta_tags:
            publish_date = date_meta_tags[0].get("content", "Date not available")

        # Extract main content (this is a simplified approach)
        # A more robust solution would use libraries like newspaper3k or trafilatura
        # or implement more sophisticated content extraction algorithms

        # Remove script, style tags and comments
        for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
            element.decompose()

        # Find the main content - this is a heuristic approach
        main_content = None

        # Try to find article tag first
        article = soup.find("article")
        if article:
            main_content = article

        # If no article tag, look for main tag
        if not main_content:
            main_content = soup.find("main")

        # If neither article nor main, look for div with common content class names
        if not main_content:
            content_divs = soup.select(
                "div.content, div.post, div.post-content, div.entry, div.entry-content, div.article-body"
            )
            if content_divs:
                main_content = content_divs[0]

        # If still no main content, use the body
        if not main_content:
            main_content = soup.body

        # Extract text from main content
        if main_content:
            paragraphs = main_content.find_all("p")
            content = " ".join([p.text for p in paragraphs])
        else:
            content = "Could not extract content from this article"

        if (
            not content or len(content) < 100
        ):  # If content is too short, it's probably not the main content
            # Fall back to extracting all visible text from the body
            content = soup.body.get_text(separator=" ", strip=True)

        return {
            "title": title,
            "publish_date": publish_date,
            "content": content,
            "source_type": "article",
        }
    except Exception as e:
        logger.error(f"Error extracting article content: {str(e)}")
        return {"error": f"Failed to extract content: {str(e)}"}


def extract_content(url):
    """Extract content from a URL (either YouTube or article)"""
    if not url:
        return {"error": "URL is empty"}

    if is_youtube_url(url):
        return get_youtube_content(url)
    else:
        return get_article_content(url)
