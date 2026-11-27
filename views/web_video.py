import streamlit as st

from src.database import save_note
from src.website_processor import extract_website_text, generate_website_notes
from src.youtube_processor import extract_youtube_transcript
from src.ui_theme import page_header

st.markdown(page_header("🌐", "Web & video notes",
                        "Paste a website or a YouTube lecture link and get notes you can save."),
            unsafe_allow_html=True)


def show_generated_notes(state_key):
    item = st.session_state.get(state_key)
    if not item:
        return
    st.subheader(item["title"])
    st.caption(f"Source: {item['source']}")
    st.markdown(item["notes"])
    with st.expander("View the extracted text"):
        st.write(item["text"])
    if st.button("💾 Save to Smart Notes", key=f"save_{state_key}"):
        save_note(item["title"], item["subject"], item["notes"])
        st.success("Saved. Open Smart Notes to see it.")


def website_tab():
    st.caption("Some websites block automatic reading. If that happens, copy the text into a new note by hand.")
    url = st.text_input("Website URL", placeholder="https://en.wikipedia.org/wiki/Machine_learning", key="website_url")
    if st.button("Generate website notes", key="generate_website_notes", type="primary"):
        if not url.strip():
            st.warning("Enter a website URL first.")
        else:
            try:
                with st.spinner("Reading the website and writing notes..."):
                    website = extract_website_text(url)
                    text = website["text"][:12000]
                    notes = generate_website_notes(text)
                st.session_state["web_notes"] = {
                    "title": website["title"], "source": website["url"],
                    "notes": notes, "text": text, "subject": "Website",
                }
            except Exception as error:
                st.session_state.pop("web_notes", None)
                st.error(f"Website processing failed: {error}")
    show_generated_notes("web_notes")


def youtube_tab():
    st.caption("Works only for videos that have captions (a transcript).")
    url = st.text_input("YouTube video URL", placeholder="https://www.youtube.com/watch?v=...", key="youtube_url")
    if st.button("Generate YouTube notes", key="generate_youtube_notes", type="primary"):
        if not url.strip():
            st.warning("Enter a YouTube video URL first.")
        else:
            try:
                with st.spinner("Getting the transcript and writing notes..."):
                    video = extract_youtube_transcript(url)
                    text = video["text"][:12000]
                    notes = generate_website_notes(text)
                st.session_state["youtube_notes"] = {
                    "title": f"YouTube notes ({video['video_id']})", "source": video["url"],
                    "notes": notes, "text": text, "subject": "YouTube",
                }
            except Exception as error:
                st.session_state.pop("youtube_notes", None)
                st.error(f"YouTube processing failed: {error}")
    show_generated_notes("youtube_notes")


t1, t2 = st.tabs(["🌐 Website", "🎥 YouTube video"])
with t1:
    website_tab()
with t2:
    youtube_tab()
