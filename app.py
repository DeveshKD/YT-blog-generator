import streamlit as st
import re
from graph_generator import BlogGenGraph

st.title('Blog Generator')
st.write("Generates title and content for given Youtube video.")

# Initialize session state
if "blog_state" not in st.session_state:
    st.session_state.blog_state = {
        "yt_url": None,
        "transcript": None,
        "blog_title": None,
        "blog_content": None,
        "regenerate_status": None,
        "message": ["Session started."],
        "valid_yt_url": False
    }
thread = {"configurable": {"thread_id": "1"}}
youtube_pattern = re.compile(
    r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$', re.IGNORECASE
)
yt_url = st.text_input("Enter YouTube URL:", key="yt_url")
if yt_url:
    if youtube_pattern.match(yt_url):
        st.session_state.blog_state["yt_url"] = yt_url
        st.session_state.blog_state["valid_yt_url"] = True
    else:
        st.write("Invalid YouTube URL. Please enter a valid YouTube URL.")
graph = BlogGenGraph().create_graph()
if st.button("Generate Blog"):
    with st.spinner("Generating blog title and content..."):
        new_state = graph.invoke(st.session_state.blog_state, thread)
        st.session_state.blog_state = new_state
        st.title("Generated Blog:")
        st.markdown(st.session_state.blog_state["blog_content"])
        st.write("next state", graph.get_state(thread).next)

if st.session_state.blog_state["blog_content"]:
    st.write("ANY FEEDBACK?")
    feedback = st.text_input("Feedback:")