import streamlit as st
import re
import base64
from graph_generator import BlogGenGraph

st.title('Blog Generator')
st.write("Generates title and content for given Youtube video.")
graph = BlogGenGraph().create_graph()

def get_download_link(markdown_text, filename="blog_content.md"):
    """Generates a link to download the markdown text as a file"""
    b64 = base64.b64encode(markdown_text.encode()).decode()
    href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}">Download Markdown File</a>'
    return href

if "blog_state" not in st.session_state:
    st.session_state.blog_state = {
        "yt_url": None,
        "transcript": None,
        "blog_title": None,
        "blog_content": None,
        "regenerate_status": None,
        "message": ["Session started."],
        "feedback": None,
        "valid_yt_url": False,
        "next_state": None
    }

if "waiting_for_feedback" not in st.session_state.blog_state:
    st.session_state.blog_state["waiting_for_feedback"] = False

thread = {"configurable": {"thread_id": "1"}}
youtube_pattern = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$', re.IGNORECASE
)

if st.session_state.blog_state.get("next_state") == "end":
    st.success("Blog generation completed!")
    
    if st.session_state.blog_state.get("blog_content"):
        st.title("Your Generated Blog:")
        st.markdown(st.session_state.blog_state["blog_content"])
        
        st.markdown(get_download_link(st.session_state.blog_state["blog_content"]), unsafe_allow_html=True)
    
    if st.button("Start Over"):
        st.session_state.blog_state = {
            "yt_url": None,
            "transcript": None,
            "blog_title": None,
            "blog_content": None,
            "regenerate_status": None,
            "message": ["Session started."],
            "feedback": None,
            "valid_yt_url": False,
            "next_state": None,
            "waiting_for_feedback": False
        }
        st.rerun()
else:
    if st.session_state.blog_state["blog_content"] is None:
        yt_url = st.text_input("Enter YouTube URL:", key="yt_url")
        if yt_url:
            if youtube_pattern.match(yt_url):
                st.session_state.blog_state["yt_url"] = yt_url
                st.session_state.blog_state["valid_yt_url"] = True
            else:
                st.error("Invalid YouTube URL. Please enter a valid YouTube URL.")
                st.session_state.blog_state["valid_yt_url"] = False
        
        generate_button = st.button("Generate Blog", disabled=not st.session_state.blog_state.get("valid_yt_url", False))
        if generate_button:
            with st.spinner("Generating blog title and content..."):
                new_state = graph.invoke(st.session_state.blog_state, thread)
                st.session_state.blog_state = new_state
                st.rerun()
    
    elif st.session_state.blog_state["blog_content"] is not None:
        st.title("Generated Blog:")
        st.markdown(st.session_state.blog_state["blog_content"])
        
        st.markdown(get_download_link(st.session_state.blog_state["blog_content"]), unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        if st.session_state.blog_state.get("waiting_for_feedback", False):
            feedback = st.text_area("Please provide detailed feedback for regeneration:", 
                                    key="feedback_input", 
                                    height=150)
            if st.button("Submit Feedback & Regenerate"):
                if feedback:
                    st.session_state.blog_state["feedback"] = feedback
                    st.session_state.blog_state["regenerate_status"] = "yes"
                    st.session_state.blog_state["waiting_for_feedback"] = False
                    
                    graph.update_state(thread, {
                        "regenerate_status": "yes", 
                        "feedback": feedback, 
                        "next_state": "regenerate"
                    }, as_node="human_feedback")
                    
                    with st.spinner("Regenerating blog based on your feedback..."):
                        new_state = graph.invoke(st.session_state.blog_state, thread)
                        st.session_state.blog_state = new_state
                        st.rerun()
                else:
                    st.warning("Please provide feedback before regenerating.")
            
            if st.button("Cancel", key="cancel_feedback"):
                st.session_state.blog_state["waiting_for_feedback"] = False
                st.rerun()
                
        else:
            with col1:
                if st.button("Regenerate?"):
                    st.session_state.blog_state["waiting_for_feedback"] = True
                    st.rerun()
            
            with col2:
                if st.button("Accept & Finish"):
                    graph.update_state(thread, {"regenerate_status": "no", "next_state": "end"}, as_node="human_feedback")
                    st.session_state.blog_state["next_state"] = "end"
                    st.rerun()