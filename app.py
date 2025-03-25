import os
import streamlit as st
import base64
from datetime import datetime
from pathlib import Path

from content_extractor import extract_content
from summarizer import generate_summary
from audio_generator import generate_audio

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
    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    b64_audio = base64.b64encode(audio_bytes).decode()
    filename = os.path.basename(file_path)

    href = f'<a href="data:audio/mp3;base64,{b64_audio}" download="{filename}">Download Audio File</a>'
    return href


def main():
    st.markdown(
        '<div class="main-header">Smart Content Summary & Audio Generator</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Extract insights from YouTube videos and articles with AI-powered summaries and audio conversion."
    )

    # Session state initialization
    if "content_data" not in st.session_state:
        st.session_state.content_data = None
    if "summary_data" not in st.session_state:
        st.session_state.summary_data = None
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = None
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    if "processing_type" not in st.session_state:
        st.session_state.processing_type = None

    # Create a form for input
    with st.form("content_form"):
        # URL input
        url = st.text_input(
            "Enter YouTube URL or article/blog link:",
            placeholder="https://example.com/article or YouTube link",
            disabled=st.session_state.is_processing,
        )

        # Summary type selection
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

        # Map UI options to internal keys
        summary_type_map = {
            "Quick Takeaways": "quick",
            "Deep Dive": "deep_dive",
            "Key Quotes": "key_quotes",
            "Key Principles/Lessons": "key_principles",
        }

        # Submit button
        if st.form_submit_button(
            "Generate Summary", type="primary", disabled=st.session_state.is_processing
        ):
            if url:
                st.session_state.is_processing = True
                st.session_state.processing_type = "summary"
                st.rerun()

    # Handle processing after rerun
    if st.session_state.is_processing and st.session_state.processing_type == "summary":
        with st.spinner("Processing..."):
            # Extract content
            content_data = extract_content(url)

            if "error" in content_data:
                st.error(f"Error: {content_data['error']}")
            else:
                st.session_state.content_data = content_data
                # Generate summary
                summary_data = generate_summary(
                    content_data["content"],
                    content_data["title"],
                    summary_type_map[summary_type],
                )

                if "error" in summary_data:
                    st.error(f"Error: {summary_data['error']}")
                else:
                    st.session_state.summary_data = summary_data
                    st.session_state.audio_data = None

        st.session_state.is_processing = False
        st.session_state.processing_type = None
        st.rerun()

    # Display content metadata and summary
    if st.session_state.content_data and st.session_state.summary_data:
        content_data = st.session_state.content_data
        summary_data = st.session_state.summary_data

        if "error" not in content_data and "error" not in summary_data:
            # Display metadata
            st.markdown(f"#### Title: {content_data['title']}")
            st.markdown(f"#### Published Date: {content_data['publish_date']}")
            st.markdown("---")

            # Display summary
            st.markdown(
                f'<div class="sub-header">Summary ({summary_type})</div>',
                unsafe_allow_html=True,
            )
            st.markdown(summary_data["summary"])
            st.markdown("</div>", unsafe_allow_html=True)

            # Audio generation button
            if st.button(
                "Create Audio Version",
                type="primary",
                disabled=st.session_state.is_processing,
            ):
                st.session_state.is_processing = True
                st.session_state.processing_type = "audio"
                st.rerun()

    # Handle audio processing after rerun
    if st.session_state.is_processing and st.session_state.processing_type == "audio":
        with st.spinner("Generating audio..."):
            audio_data = generate_audio(
                summary_data["summary"], content_data["title"], AUDIO_DIR
            )
            st.session_state.audio_data = audio_data

        st.session_state.is_processing = False
        st.session_state.processing_type = None
        st.rerun()

    # Display audio
    if st.session_state.audio_data:
        audio_data = st.session_state.audio_data

        if "error" in audio_data:
            st.error(f"Error: {audio_data['error']}")
        else:
            st.markdown("---")
            st.markdown(
                f'<div class="sub-header">Summary Audio</div>', unsafe_allow_html=True
            )

            if "note" in audio_data:
                st.info(audio_data["note"])

            # Display audio player
            audio_file = open(audio_data["audio_path"], "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")

            # Display download link
            st.markdown(
                get_audio_file_link(audio_data["audio_path"]), unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()
