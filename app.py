import os
import time
import streamlit as st
import base64
import logging
from pathlib import Path

from content_extractor import extract_content
from summarizer import generate_audio_summary, generate_summary
from audio_generator import generate_audio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up the page configuration
st.set_page_config(
    page_title="Smart Content Summary & Audio Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Create audio directory if it doesn't exist
AUDIO_DIR = "audio_files"
Path(AUDIO_DIR).mkdir(parents=True, exist_ok=True)
logger.info(f"Created/verified audio directory: {AUDIO_DIR}")

# Custom CSS styles
st.markdown(
    """
<style>
    .main-header {
        font-size: 30px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 20px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .content-box {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .metadata-box {
        background-color: #e8f4f8;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 4px solid #2196F3;
    }
    .stAudio {
        margin-top: 10px;
    }
    .stAlert {
        margin-top: 15px;
    }
</style>
""",
    unsafe_allow_html=True,
)


def get_audio_file_link(file_path):
    """Generate a download link for the audio file"""
    logger.info(f"Generating download link for audio file: {file_path}")
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    b64_audio = base64.b64encode(audio_bytes).decode()
    filename = os.path.basename(file_path)

    href = f'<a href="data:audio/mp3;base64,{b64_audio}" download="{filename}">Download Audio File</a>'
    return href


def main():
    max_age_minutes = 3
    logger.info("Starting application")

    root_dir = Path(__file__).resolve().parent
    logger.info(f"Root directory: {root_dir}")

    audio_files_dir = root_dir / AUDIO_DIR
    logger.info(f"Audio files directory: {audio_files_dir}")

    current_time = time.time()
    for file_path in Path(root_dir / AUDIO_DIR).glob("*.mp3"):
        file_creation_time = os.path.getctime(file_path)
        file_age_minutes = (current_time - file_creation_time) / 60

        if file_age_minutes >= max_age_minutes:
            try:
                logger.info(f"Attempting to delete old audio file: {file_path}")
                os.remove(file_path)
                logger.info(f"Successfully deleted old audio file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting old audio file {file_path}: {str(e)}")

    st.markdown(
        '<div class="main-header">Smart Content Summary & Audio Generator</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Extract insights from YouTube videos and articles with AI-powered summaries and audio conversion."
    )
    st.markdown(
        "Only videos with captions available in English are allowed to be processed."
    )

    # Initialize session state
    if "content_data" not in st.session_state:
        st.session_state.content_data = None
        logger.info("Initialized content_data in session state")
    if "summary_data" not in st.session_state:
        st.session_state.summary_data = None
        logger.info("Initialized summary_data in session state")
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = None
        logger.info("Initialized audio_data in session state")
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
        logger.info("Initialized is_processing in session state")
    if "processing_type" not in st.session_state:
        st.session_state.processing_type = None
        logger.info("Initialized processing_type in session state")

    with st.form("content_form"):
        url = st.text_input(
            "Enter YouTube URL or article/blog link:",
            placeholder="https://example.com/article or YouTube link",
            disabled=st.session_state.is_processing,
        )

        summary_type = st.radio(
            "Select summary style:",
            options=[
                "Quick Takeaways",
                "Deep Dive",
                "Key Quotes",
                "Key Principles/Lessons",
            ],
            index=0,
            disabled=st.session_state.is_processing,
        )

        summary_type_map = {
            "Quick Takeaways": "quick",
            "Deep Dive": "deep_dive",
            "Key Quotes": "key_quotes",
            "Key Principles/Lessons": "key_principles",
        }

        if st.form_submit_button(
            "Generate Summary", type="primary", disabled=st.session_state.is_processing
        ):
            if url:
                logger.info(
                    f"Form submitted with URL: {url} and summary type: {summary_type}"
                )
                st.session_state.is_processing = True
                st.session_state.processing_type = "summary"
                st.rerun()

    if st.session_state.is_processing:
        if st.session_state.processing_type == "summary":
            logger.info("Starting content extraction and summary generation")
            with st.spinner("Processing..."):
                content_data = extract_content(url)
                logger.info(
                    f"Content extraction completed. Title: {content_data.get('title', 'N/A')}"
                )

                if "error" in content_data:
                    error_msg = f"Error in content extraction: {content_data['error']}"
                    logger.error(error_msg)
                    st.error(error_msg)
                    st.session_state.is_processing = False
                    st.session_state.processing_type = None
                else:
                    st.session_state.content_data = content_data
                    logger.info("Starting summary generation")
                    summary_data = generate_summary(
                        content_data["content"],
                        content_data["title"],
                        content_data["publish_date"],
                        summary_type_map[summary_type],
                    )

                    if "error" in summary_data:
                        error_msg = (
                            f"Error in summary generation: {summary_data['error']}"
                        )
                        logger.error(error_msg)
                        st.error(error_msg)
                        st.session_state.is_processing = False
                        st.session_state.processing_type = None
                    else:
                        st.session_state.summary_data = summary_data
                        logger.info("Summary generation completed successfully")
                        st.session_state.processing_type = "audio"
                        st.rerun()

        elif st.session_state.processing_type == "audio":
            if st.session_state.content_data and st.session_state.summary_data:
                logger.info("Starting audio generation")
                with st.spinner("Generating audio..."):
                    audio_summary = generate_audio_summary(
                        content=st.session_state.summary_data["summary"],
                        title=st.session_state.content_data["title"],
                        summary_type=summary_type_map[summary_type],
                    )

                    if not audio_summary:
                        logger.info("Using original summary for audio generation")
                        audio_summary = st.session_state.summary_data["summary"]

                    audio_data = generate_audio(
                        text=audio_summary,
                        title=st.session_state.content_data["title"],
                        output_dir=AUDIO_DIR,
                    )
                    st.session_state.audio_data = audio_data
                    logger.info(
                        f"Audio generation completed. File path: {audio_data.get('audio_path', 'N/A')}"
                    )

                st.session_state.is_processing = False
                st.session_state.processing_type = None
                st.rerun()

    if (
        st.session_state.content_data
        and st.session_state.summary_data
        and st.session_state.audio_data
    ):
        logger.info("Displaying results")
        content_data = st.session_state.content_data
        summary_data = st.session_state.summary_data
        audio_data = st.session_state.audio_data

        if (
            "error" not in content_data
            and "error" not in summary_data
            and "error" not in audio_data
        ):
            # Display metadata
            st.markdown(f"#### Title: {content_data['title']}")
            st.markdown(
                f"#### Published Date: {summary_data['published_date'] if summary_data['published_date'] else content_data['publish_date']}"
            )
            st.markdown("---")

            # Display audio first
            st.markdown(
                f'<div class="sub-header">Summary Audio</div>', unsafe_allow_html=True
            )

            if "note" in audio_data:
                logger.info(f"Audio generation note: {audio_data['note']}")
                st.info(audio_data["note"])

            audio_file = open(audio_data["audio_path"], "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")

            st.markdown(
                get_audio_file_link(audio_data["audio_path"]), unsafe_allow_html=True
            )

            # Display summary after audio
            st.markdown("---")
            st.markdown(
                f'<div class="sub-header">Summary ({summary_type})</div>',
                unsafe_allow_html=True,
            )
            st.markdown(summary_data["summary"])
            st.markdown("</div>", unsafe_allow_html=True)
            logger.info("Results displayed successfully")


if __name__ == "__main__":
    main()
