import streamlit as st

from src import workspace as ws
from src.database import save_note, get_notes, update_note, delete_note
from src.notes_generator import generate_notes
from src.ui_theme import page_header

st.markdown(page_header("📝", "Smart Notes",
                        "Write, generate, edit and keep your study notes in one place."),
            unsafe_allow_html=True)


def library_tab():
    notes = get_notes()
    if not notes:
        st.info("You have no saved notes yet. Open “New note” or “Generate from PDFs” to make the first one.")
        return
    for note in notes:
        with st.expander(f"📄 {note['title']}  |  {note['subject'] or 'No subject'}"):
            st.caption(f"Created: {note['created_at']}")
            st.write(note["content"])
            st.divider()
            st.write("✏️ Edit this note")
            with st.form(f"edit_note_{note['id']}"):
                edit_title = st.text_input("Title", value=note["title"], key=f"title_{note['id']}")
                edit_subject = st.text_input("Subject", value=note["subject"] or "", key=f"subject_{note['id']}")
                edit_content = st.text_area("Content", value=note["content"], height=150, key=f"content_{note['id']}")
                if st.form_submit_button("Update note"):
                    if not edit_title.strip() or not edit_content.strip():
                        st.error("Title and content cannot be empty.")
                    else:
                        update_note(note["id"], edit_title.strip(), edit_subject.strip(), edit_content.strip())
                        st.success("Note updated.")
                        st.rerun()
            if st.button("🗑️ Delete note", key=f"delete_{note['id']}"):
                delete_note(note["id"])
                st.success("Note deleted.")
                st.rerun()


def new_note_tab():
    with st.form("create_note_form"):
        new_title = st.text_input("Note title", placeholder="e.g. Introduction to Machine Learning")
        new_subject = st.text_input("Subject", placeholder="e.g. Artificial Intelligence")
        new_content = st.text_area("Note content", placeholder="Write your study notes here...", height=220)
        if st.form_submit_button("💾 Save note", type="primary"):
            if not new_title.strip() or not new_content.strip():
                st.error("Enter both a title and the note content.")
            else:
                save_note(new_title.strip(), new_subject.strip(), new_content.strip())
                st.success("Note saved. Open “My notes” to see it.")
                st.rerun()


def generate_tab():
    if not ws.has_docs():
        ws.show_empty("generate notes with AI")
        return

    if st.button("✨ Generate notes from my PDFs", type="primary"):
        with st.spinner("AI is preparing your study notes..."):
            try:
                generated = generate_notes(ws.all_document_text())
                if generated.startswith("Error"):
                    st.error(generated)
                else:
                    first = list(ws.documents().values())[0]["name"].rsplit(".", 1)[0]
                    st.session_state["generated_notes_editor"] = generated
                    st.session_state["generated_notes_title"] = first + " - Study Notes"
            except Exception as e:
                st.error(f"Could not generate notes: {e}")

    if "generated_notes_editor" in st.session_state:
        title = st.text_input("Generated note title", key="generated_notes_title")
        st.text_area("Review and edit your generated notes", height=360, key="generated_notes_editor")
        if st.button("💾 Save AI-generated notes"):
            if title.strip() and st.session_state["generated_notes_editor"].strip():
                save_note(title.strip(), "AI Generated", st.session_state["generated_notes_editor"])
                del st.session_state["generated_notes_editor"]
                del st.session_state["generated_notes_title"]
                st.success("Saved. Open “My notes” to see it.")
                st.rerun()
            else:
                st.error("Enter a title and some note content.")


def main():
    t1, t2, t3 = st.tabs(["📚 My notes", "➕ New note", "✨ Generate from PDFs"])
    with t1:
        library_tab()
    with t2:
        new_note_tab()
    with t3:
        generate_tab()


main()
