import json
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

quick_summary_system_prompt = """
## Purpose
Generate a concise bullet-point summary of the key points with validated publication date.

## Input Requirements
Provide the following three pieces of information:
1. **Title**: The original title of the content
2. **Content**: Full text of the article, blog post, or document
3. **Published Date**: Date of publication

## Formatting Instructions
- Ensure content is clear and complete
- Date should be in a recognizable format (e.g., YYYY-MM-DD, DD/MM/YYYY, Month DD, YYYY)
- Include full text to enable accurate summarization


## Expected Output
```json
{
  "response": {
    "summary": <Concise summary capturing key points in MARKDOWN format>",
    "published_date": <YYYY-MM-DD>
  }
}
```

## Notes
- If date is unrecognizable, it will be set to `null`
- Summary will extract most significant sentences
- Aim for clarity and representativeness in content provided
"""

deep_dive_system_prompt = """
## Purpose  
Generate a comprehensive and detailed summary that thoroughly explains all major points, their significance, and any relevant context, organized into logical sections with headings.  

## Input Requirements  
Provide the following three pieces of information:  
1. **Title**: The original title of the content  
2. **Content**: Full text of the article, blog post, or document  
3. **Published Date**: Date of publication  

## Formatting Instructions  
- Ensure content is fully captured with in-depth explanations  
- Structure the summary using clear headings and subheadings for readability  
- Date should be in a recognizable format (e.g., YYYY-MM-DD, DD/MM/YYYY, Month DD, YYYY)  
- Include full text to enable accurate summarization  

## Expected Output  
```json  
{  
  "response": {  
    "summary": "<Detailed summary organized with headings and subheadings in MARKDOWN format>",  
    "published_date": "<YYYY-MM-DD>"  
  }  
}  
```  

## Notes  
- If date is unrecognizable, it will be set to `null`  
- Summary should provide context, background, and implications of key points  
- Maintain clarity while ensuring depth and completeness  
"""

key_quotes_system_prompt = """
## Purpose  
Extract the most impactful and relevant direct quotes from the content that best represent key ideas, arguments, or insights.  

## Input Requirements  
Provide the following three pieces of information:  
1. **Title**: The original title of the content  
2. **Content**: Full text of the article, blog post, or document  
3. **Published Date**: Date of publication  

## Formatting Instructions  
- Extract direct quotes that highlight critical points, arguments, or insights  
- Provide quotes verbatim without modification  
- Date should be in a recognizable format (e.g., YYYY-MM-DD, DD/MM/YYYY, Month DD, YYYY)  
- Include full text to ensure accurate extraction  

## Expected Output  
```json  
{  
  "response": {  
    "summary": "<Extracted quote in MARKDOWN format>",  
    "published_date": "<YYYY-MM-DD>"  
  }  
}  
``` 

## Notes  
- If date is unrecognizable, it will be set to `null`.
"""

key_principles_system_prompt = """
Here’s the prompt for the **'Key Principles'** summary type:  

```  
## Purpose  
Identify and explain the fundamental principles, lessons, or insights from the content, extracting 3-5 core principles with clear explanations of their significance.  

## Input Requirements  
Provide the following three pieces of information:  
1. **Title**: The original title of the content  
2. **Content**: Full text of the article, blog post, or document  
3. **Published Date**: Date of publication  

## Formatting Instructions  
- Extract 3-5 fundamental principles or lessons  
- Format as numbered points with a brief but clear explanation of each principle’s significance  
- Date should be in a recognizable format (e.g., YYYY-MM-DD, DD/MM/YYYY, Month DD, YYYY)  
- Include full text to ensure accurate extraction  

## Expected Output  
```json  
{  
  "response": {  
    "summary": "<Core principles or lessons with explanations in MARKDOWN format>",  
    "published_date": "<YYYY-MM-DD>"  
  }  
}  
```  

## Notes  
- If date is unrecognizable, it will be set to `null`  
- Principles should capture the most essential insights or lessons from the content  
- Ensure clarity and conciseness while maintaining depth in explanations
"""

audio_summary_system_prompt = """
Generate a summary for the audio using the following details:

Title: Summary Title
Content: Summary Content
Summary Type: Summary Type based on summary is created

Instructions:
1. Analyze the provided content thoroughly.
2. Generate a concise summary that aligns with the specified summary type.
3. Ensure the summary is suitable for audio narration and easy to understand.
4. Return the response in JSON format as shown below.

Expected JSON Response Format:
{
  "response": {
    "summary": "<Summary based on provided summary type in simple text>"
  }
}
"""


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


def generate_summary(
    content: str, title: str, publish_date: str, summary_type: str = "quick"
) -> dict:
    """Generate a summary using OpenAI's API based on the selected summary type"""
    if not content:
        return {"error": "No content provided for summarization"}

    # Truncate content if needed
    truncated_content = truncate_content(content, max_tokens=120000)

    # Define prompts for different summary types
    prompts = {
        "quick": quick_summary_system_prompt,
        "deep_dive": deep_dive_system_prompt,
        "key_quotes": key_quotes_system_prompt,
        "key_principles": key_principles_system_prompt,
    }

    if summary_type not in prompts:
        return {"error": f"Invalid summary type: {summary_type}"}

    user_prompt = """
# Here is the content to summarize :

## Input Values 
Title: {variable_title}
Content: {variable_content}
Published Date: {variable_publish_date}
"""
    user_prompt = (
        user_prompt.replace("{variable_title}", title)
        .replace("{variable_content}", truncated_content)
        .replace("{variable_publish_date}", publish_date)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": prompts[summary_type],
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content

        json_response = json.loads(response_text)
        summary = json_response["response"]["summary"]
        published_date = json_response["response"]["published_date"]

        return {
            "summary": summary,
            "summary_type": summary_type,
            "published_date": published_date,
        }

    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return {"error": f"Failed to generate summary: {str(e)}"}


def generate_audio_summary(content: str, title: str, summary_type: str) -> str | None:
    """
    Generate a summary of the content in audio format
    """
    if not (content and title and summary_type):
        return None

    user_prompt = """
# Here is the content to summarize for audio :

## Input Values 
Title: {variable_title}
Content: {variable_content}
Summary Type : {variable_summary_type}
"""
    user_prompt = (
        user_prompt.replace("{variable_title}", title)
        .replace("{variable_content}", content)
        .replace("{variable_summary_type}", summary_type)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-3.5-turbo" for lower cost
            messages=[
                {
                    "role": "system",
                    "content": audio_summary_system_prompt,
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=1,
            response_format={"type": "json_object"},
        )

        response_text = response.choices[0].message.content

        json_response = json.loads(response_text)
        return json_response["response"]["summary"]

    except Exception as e:
        logger.error(f"Error generating audio summary: {str(e)}")
        return {"error": f"Failed to generate audio summary: {str(e)}"}
