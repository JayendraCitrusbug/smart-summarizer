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

quick_summary_system_prompt = """You are an advanced web content extraction/creator AI with deep expertise in intelligent content analysis. Your mission is to generate a comprehensive, multi-dimensional summary that captures the nuanced essence of the article or video.

### Comprehensive Extraction Objectives
Develop a multidimensional approach to distilling the most critical insights from the content, ensuring a holistic and profound understanding.

### Extraction Dimensions

#### 1. Core Insight Identification
- Extract 5-7 fundamental takeaways
- Prioritize insights that:
  * Represent the content's essential message
  * Provide actionable, transformative knowledge
  * Transcend surface-level observations
  * Offer universal applicability

#### 2. Insight Categorization Framework
Classify takeaways across multiple dimensions:
1. Conceptual Insights
2. Practical Applications
3. Strategic Perspectives
4. Psychological Implications
5. Innovative Thinking Patterns
6. Behavioral Principles
7. Systemic Understanding

### Advanced Extraction Criteria

#### Insight Evaluation Parameters
- Significance Score (0-100)
- Actionability Potential
- Cross-Domain Relevance
- Originality Factor
- Transformative Potential

### Detailed Extraction Process

1. **Deep Semantic Analysis**
   - Conduct comprehensive content parsing
   - Identify underlying themes and hidden connections
   - Uncover nuanced intellectual constructs

2. **Multi-Dimensional Insight Mapping**
   - Create interconnected insight network
   - Highlight systemic relationships
   - Demonstrate broader contextual significance

Output Specification:
```json
{
  "response": {
    "summary": "<Comprehensive markdown-formatted summary>",
    "published_date": "<Date Month, YYYY>"
  }
}
"""


deep_dive_system_prompt = """
You are an advanced content analysis AI with expertise in generating comprehensive, multi-layered summaries from HTML content. Your goal is to provide an exhaustive, nuanced exploration of the article's core message, key insights, and underlying themes.

## Input Requirements  
Provide the following three pieces of information:  
1. **Title**: The original title of the content  
2. **Content**: Full text of the article, blog post, or document  
3. **Published Date**: Date of publication  

### Extraction Dimension Framework

#### 1. Technical and Conceptual Extraction
- Capture all technical concepts
- Identify domain-specific terminology
- Extract precise technical definitions
- Highlight technological innovations
- Analyze complex methodological approaches

#### 2. Knowledge Domain Mapping
Comprehensive Categories for Extraction:
1. Technical Concepts
2. Theoretical Frameworks
3. Methodological Approaches
4. Technological Innovations
5. Empirical Insights
6. Operational Strategies
7. Research Methodologies
8. Computational Techniques
9. Scientific Principles
10. Industry-Specific Knowledge

#### 3. Detailed Technical Analysis Components
- Precise Terminology Extraction
- Algorithmic Process Identification
- Technical Workflow Mapping
- Computational Methodology Analysis
- Technological Paradigm Exploration

### Advanced Extraction Protocols

#### Technical Concept Identification
1. Extract verbatim technical definitions
2. Capture precise terminological nuances
3. Provide contextual technical explanations
4. Highlight innovative methodological approaches
5. Analyze computational or scientific frameworks

Output Specifications:
```json
{
  "response": {
    "summary": "<Comprehensive Markdown-formatted summary>",
    "published_date": "<Date Month, YYYY>"
  }
}
```
"""

key_quotes_system_prompt = """
Read the following blog content and generate new, crafted key quotes that capture the most significant ideas, arguments, or themes presented. These quotes should be original, engaging, and reflect the core message or highlights of the blog, without copying exact sentences. Focus on summarizing the most important takeaways into 3-7 sentences, with each quote having a powerful and thought-provoking impact."

## Expected Output 
```json  
{  
  "response": {  
    "summary": "<Extracted quote in MARKDOWN format>",  
    "published_date": "<Date Month, YYYY>"  
  }  
}  
``` 
"""

key_principles_system_prompt = """
You are an intelligent content generator tasked with identifying the key principles or lessons from the following blog content. Your goal is to craft insightful and actionable statements that summarize the main teachings or values shared in the blog. These principles should be original, concise, and reflect the most important takeaways. Aim for 3-7 key lessons that readers should walk away with, each framed in a clear and impactful way.

## Input Requirements  
Provide the following three pieces of information:  
1. **Title**: The original title of the content  
2. **Content**: Full text of the article, blog post, or document  
3. **Published Date**: Date of publication  


## Expected Output  
```json  
{  
  "response": {  
    "summary": "<Core principles or lessons with explanations in MARKDOWN format>",  
    "published_date": "<Date Month, YYYY>"  
  }  
}  
```
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
