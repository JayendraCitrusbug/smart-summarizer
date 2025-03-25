import os
import time
import streamlit as st
import base64
from pathlib import Path

from content_extractor import extract_content
from summarizer import generate_audio_summary, generate_summary
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
    max_age_minutes = 3

    current_time = time.time()
    for file_path in Path(AUDIO_DIR).glob("*.mp3"):
        file_creation_time = os.path.getctime(file_path)

        file_age_minutes = (current_time - file_creation_time) / 60

        if file_age_minutes >= max_age_minutes:
            try:
                # Delete the file
                os.remove(file_path)
            except Exception as e:
                pass

    st.markdown(
        '<div class="main-header">Smart Content Summary & Audio Generator</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Extract insights from YouTube videos and articles with AI-powered summaries and audio conversion."
    )

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
                st.session_state.is_processing = True
                st.session_state.processing_type = "summary"
                st.rerun()

    if st.session_state.is_processing:
        if st.session_state.processing_type == "summary":
            with st.spinner("Processing..."):
                content_data = extract_content(url)

                if "error" in content_data:
                    st.error(f"Error: {content_data['error']}")
                    st.session_state.is_processing = False
                    st.session_state.processing_type = None
                else:
                    st.session_state.content_data = content_data
                    summary_data = generate_summary(
                        content_data["content"],
                        content_data["title"],
                        content_data["publish_date"],
                        summary_type_map[summary_type],
                    )

                    if "error" in summary_data:
                        st.error(f"Error: {summary_data['error']}")
                        st.session_state.is_processing = False
                        st.session_state.processing_type = None
                    else:
                        st.session_state.summary_data = summary_data
                        st.session_state.processing_type = "audio"
                        st.rerun()

        elif st.session_state.processing_type == "audio":
            if st.session_state.content_data and st.session_state.summary_data:
                with st.spinner("Generating audio..."):
                    audio_summary = generate_audio_summary(
                        content=st.session_state.summary_data["summary"],
                        title=st.session_state.content_data["title"],
                        summary_type=summary_type_map[summary_type],
                    )

                    if not audio_summary:
                        audio_summary = st.session_state.summary_data["summary"]

                    audio_data = generate_audio(
                        text=audio_summary,
                        title=st.session_state.content_data["title"],
                        output_dir=AUDIO_DIR,
                    )
                    st.session_state.audio_data = audio_data

                st.session_state.is_processing = False
                st.session_state.processing_type = None
                st.rerun()

    if (
        st.session_state.content_data
        and st.session_state.summary_data
        and st.session_state.audio_data
    ):
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


if __name__ == "__main__":
    main()
