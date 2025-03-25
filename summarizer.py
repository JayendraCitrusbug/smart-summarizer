import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def truncate_content(content, max_tokens=8000):
    """Truncate content to fit within token limits for OpenAI API"""
    # This is a simple approximation - 1 token is roughly 4 chars in English
    words = content.split()
    approx_tokens = len(content) / 4

    if approx_tokens <= max_tokens:
        return content

    # Calculate rough ratio to keep
    keep_ratio = max_tokens / approx_tokens
    keep_words = int(len(words) * keep_ratio)

    # Return truncated content with note
    truncated = " ".join(words[:keep_words])
    return truncated + "\n\n[Note: Content was truncated due to length limitations]"


def generate_summary(content, title, summary_type="quick"):
    """Generate a summary using OpenAI's API based on the selected summary type"""
    if not content:
        return {"error": "No content provided for summarization"}

    # Truncate content if needed
    truncated_content = truncate_content(content, max_tokens=120000)

    # Define prompts for different summary types
    prompts = {
        "quick": f"Create a concise bullet-point summary of the key points from the following content titled '{title}':\n\n{truncated_content}\n\nFormat as a bulleted list of the most important takeaways.",
        "deep_dive": f"Create a comprehensive, detailed summary of the following content titled '{title}':\n\n{truncated_content}\n\nProvide a thorough explanation that covers all major points and their significance, organized into logical sections with headings.",
        "key_quotes": f"Extract the most significant and insightful quotes from the following content titled '{title}':\n\n{truncated_content}\n\nIdentify 5-7 direct quotes that best represent the key insights, arguments, or revelations. Format each quote on a new line with quotation marks.",
        "key_principles": f"Identify and explain the fundamental principles, lessons, or insights from the following content titled '{title}':\n\n{truncated_content}\n\nExtract 3-5 core principles or lessons and explain why each is significant. Format as numbered points with brief explanations.",
    }

    if summary_type not in prompts:
        return {"error": f"Invalid summary type: {summary_type}"}

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-3.5-turbo" for lower cost
            messages=[
                {
                    "role": "system",
                    "content": "You are a skilled content analyst and summarizer. Your task is to extract the most relevant information and present it in the requested format.",
                },
                {"role": "user", "content": prompts[summary_type]},
            ],
            temperature=0.5,
        )

        summary = response.choices[0].message.content.strip()
        return {"summary": summary, "summary_type": summary_type}

    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return {"error": f"Failed to generate summary: {str(e)}"}
