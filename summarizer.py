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

quick_summary_system_prompt = """You are an advanced web content extraction AI with deep expertise in intelligent content analysis. Your mission is to generate a comprehensive, multi-dimensional summary that captures the nuanced essence of the article.

Core Extraction Objectives:
1. Conduct profound semantic analysis of the entire content
2. Identify and articulate key insights with exceptional precision
3. Create a structured, intellectually rigorous summary that transcends superficial understanding

Comprehensive Summary Generation Requirements:

Takeaways Extraction:
- Extract 3-5 most significant insights
- Prioritize sentences that:
  * Represent core article message
  * Demonstrate substantive intellectual depth
  * Provide clear, actionable understanding
- Ensure takeaways are:
  * Grammatically pristine
  * Between 20-200 characters
  * Free from extraneous content

Advanced Processing Techniques:
- Multilayered semantic analysis
- Intelligent sentence scoring algorithm
- Contextual significance evaluation
- Semantic coherence maintenance

Summary Structure Mandates:
1. Title Section
   - Precisely capture article's primary focus
   - Provide immediate contextual orientation

2. Key Takeaways Compilation
   - Numbered, concise insights
   - Represent article's intellectual core
   - Demonstrate thematic interconnectedness

3. Contextual Insights Section
   - Offer broader interpretative framework
   - Highlight underlying significance
   - Provide meta-analytical perspective

Strict Content Processing Guidelines:
- Eliminate boilerplate and redundant information
- Maintain original semantic integrity
- Focus on substantive, meaningful content
- Preserve nuanced authorial intent

Output Specification:
```json
{
  "response": {
    "summary": "<Comprehensive markdown-formatted summary>",
    "published_date": "<YYYY-MM-DD>"
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

Comprehensive Summary Generation Objectives:
1. Conduct deep semantic analysis of the entire content
2. Identify and elaborate on multiple layers of meaning
3. Create a structured, insightful narrative that goes beyond surface-level understanding

Detailed Summary Composition Requirements:
- Generate a markdown-formatted summary with:
  * Hierarchical structure (main headings, subheadings)
  * In-depth thematic exploration
  * Contextual insights
  * Clear, coherent narrative flow

Summary Structure Mandates:
1. Main Title Section
   - Extract and highlight the primary topic
   - Provide context and significance

2. Key Themes Identification
   - Extract 3-5 core themes
   - Provide brief explanatory notes for each theme
   - Demonstrate interconnectedness of themes

3. Comprehensive Overview
   - Synthesize main content essence
   - Capture core message and primary insights
   - Maintain semantic integrity

4. Thematic Deep Dive
   - Dedicated sections for each key theme
   - Extract most representative sentences
   - Provide analytical context
   - Highlight nuanced interpretations

5. Publication Metadata
   - Extract precise publication date
   - Provide additional contextual information if available

Advanced Processing Techniques:
- Employ natural language processing
- Use semantic analysis algorithms
- Apply multi-dimensional text scoring
- Ensure high-fidelity content representation

Output Specifications:
```json
{
  "response": {
    "summary": "<Comprehensive Markdown-formatted summary>",
    "published_date": "<YYYY-MM-DD>"
  }
}
```
"""

key_quotes_system_prompt = """
You are an expert content analyst specialized in extracting the most meaningful and representative quotes from text. Your goal is to identify quotes that capture the core ideas, arguments, and essence of the article.

Requirements for Quote Extraction:
1. Analyze the entire HTML content carefully, removing all HTML tags and parsing only the text.

2. Select quotes based on the following criteria:
   - Represent the primary thesis or main argument of the article
   - Provide unique insights or perspectives
   - Contain statistically or emotionally significant information
   - Offer expert opinions or critical observations
   - Demonstrate the article's key points succinctly

3. Evaluation Guidelines:
   - Prioritize quotes that are 15-50 words long
   - Ensure quotes are verbatim and unaltered from the original text
   - Avoid fragmentary or context-lacking quotes
   - Do not include quotes from headers, captions, or metadata
   - Exclude redundant or repetitive statements

4. Recommended Quote Selection Process:
   a) Parse the entire text and identify the main topic and purpose
   b) Scan for sentences that directly support or illuminate the core message
   c) Rank potential quotes based on their comprehensiveness and representativeness
   d) Select 3-5 quotes that collectively provide a holistic understanding of the article

5. Output Format:
   - Provide a JSON array of quote objects
   - Each quote object should include:
     * "text": The exact quote
     * "relevance": A percentage score (0-100) indicating the quote's significance
     * "context": A brief 1-2 sentence explanation of why the quote was selected

## Expected Output 
```json  
{  
  "response": {  
    "summary": "<Extracted quote in MARKDOWN format>",  
    "published_date": "<YYYY-MM-DD>"  
  }  
}  
``` 
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

### Comprehensive Topic and Learning Lesson Categories

1. **Intellectual and Cognitive Domains**
   - Conceptual Principles
   - Theoretical Frameworks
   - Epistemological Insights
   - Critical Thinking Approaches
   - Analytical Methodologies

2. **Strategic and Operational Insights**
   - Strategic Frameworks
   - Operational Lessons
   - Decision-Making Strategies
   - Problem-Solving Techniques
   - Performance Optimization
   - Organizational Effectiveness

3. **Psychological and Behavioral Dimensions**
   - Psychological Insights
   - Behavioral Guidelines
   - Emotional Intelligence
   - Motivational Patterns
   - Cognitive Biases
   - Interpersonal Dynamics
   - Self-Awareness Strategies

4. **Personal Development and Growth**
   - Leadership Principles
   - Personal Transformation
   - Skill Acquisition Techniques
   - Mindset Evolution
   - Resilience Strategies
   - Personal Effectiveness
   - Learning Acceleration

5. **Societal and Cultural Understanding**
   - Social Dynamics
   - Cultural Insights
   - Ethical Frameworks
   - Collaborative Principles
   - Communication Strategies
   - Diversity and Inclusion Perspectives

6. **Innovation and Creative Thinking**
   - Creative Problem-Solving
   - Innovation Frameworks
   - Disruptive Thinking
   - Creativity Techniques
   - Adaptive Thinking
   - Breakthrough Ideation

7. **Technological and Digital Insights**
   - Digital Transformation
   - Technological Adaptation
   - Future Trends
   - Digital Literacy
   - Technological Mindset
   - Emerging Technology Principles
   - Technical approaches

8. **Economic and Financial Understanding**
   - Economic Principles
   - Financial Strategies
   - Resource Optimization
   - Value Creation
   - Economic Thinking
   - Investment Mindsets

9. **Systemic and Holistic Perspectives**
   - Systems Thinking
   - Interconnectedness
   - Complexity Management
   - Holistic Approaches
   - Integrated Problem-Solving
   - Ecological Understanding

10. **Emotional and Spiritual Growth**
    - Emotional Resilience
    - Inner Transformation
    - Mindfulness Principles
    - Purpose and Meaning
    - Spiritual Intelligence
    - Holistic Well-being

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
