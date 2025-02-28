from typing import TypedDict, Optional
from typing_extensions import Annotated
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from youtube_transcript_api import YouTubeTranscriptApi
from langgraph.graph import add_messages
from dotenv import load_dotenv
load_dotenv()
import os
from IPython.display import Image, display
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")


class BlogGenState(TypedDict):
    yt_url: Optional[str]
    transcript: Optional[str]
    blog_title: Optional[str]
    blog_content: Optional[str]
    regenerate_status: Optional[str]
    message: Annotated[list[AnyMessage], add_messages]


class Agents:
    def __init__(self):
        self.llm = ChatGroq(model="qwen-2.5-32b")
    def generate_blog(self, state: BlogGenState) -> BlogGenState:
        """
        Generates a title and content for the blog based on the transcript.
        
        Args:
            state: The current state of the workflow
            
        Returns:
            Updated state with blog title and content
        """
        transcript = state.get("transcript")
        if transcript is None:
            video_id = state["yt_url"].split("v=")[-1].split("&")[0]
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = " ".join([entry['text'] for entry in transcript_list])
            state["transcript"] = full_transcript
        regen_status = state.get("regenerate_status")
        if regen_status == "yes":
            title_regenerate_prompt = [
                SystemMessage(content="The user has chosen to regenerate the blog title. Please provide a new title for the blog post based on the transcript. PREVIOUS INSTRUCTIONS: You are an expert in generating titles for BLOG posts based on the transcripts of YouTube videos. IMPORTANT: YOU SIMPLY ONLY CREATE TITLES FOR THE BLOG. NO EXPLANATION IS REQUIRED."),
                HumanMessage(content=f"Generate a good blog title for a video with the following transcript: {state['transcript']}")
            ]
            content_regenerate_prompt = [
                SystemMessage(content="The user has chosen to regenerate the blog content. Please provide new content for the blog post based on the transcript. PREVIOUS INSTRUCTIONS: You are an expert in generating content for BLOG posts based on the transcripts of YouTube videos. IMPORTANT: YOU SIMPLY ONLY CREATE CONTENT FOR THE BLOG. THE TITLE IS ALREADY PROVIDED. Output format: Simply output the content in markdown format with appropriate headings, paragraphs, and formatting."),
                HumanMessage(content=f"Generate blog content for the title '{state['blog_title']}' based on the following transcript: {state['transcript']}")
            ]
            regenerated_title = self.llm.invoke(title_regenerate_prompt).content.strip()
            regenerated_content = self.llm.invoke(content_regenerate_prompt).content.strip()

            return {
                "blog_title": regenerated_title,
                "blog_content": regenerated_content,
                "message": state["message"] + [
                    SystemMessage(content=f"Blog title and content regenerated on the users request.")
                ]
            }

        title_prompt = [
            SystemMessage(content="You are an expert in generating titles for BLOG posts based on the transcripts of YouTube videos. IMPORTANT: YOU SIMPLY ONLY CREATE TITLES FOR THE BLOG. NO EXPLANATION IS REQUIRED."),
            HumanMessage(content=f"Generate a good blog title for a video with the following transcript: {state['transcript']}")
        ]
        blog_title = self.llm.invoke(title_prompt).content.strip()

        content_prompt = [
            SystemMessage(content="""You are an expert in generating content for BLOG posts based on the transcripts of YouTube videos. 
            IMPORTANT: YOU SIMPLY ONLY CREATE CONTENT FOR THE BLOG. THE TITLE IS ALREADY PROVIDED. 
            Output format: Simply output the content in markdown format with appropriate headings, paragraphs, and formatting."""),
            HumanMessage(content=f"Generate blog content for the title '{blog_title}' based on the following transcript: {state['transcript']}")
        ]
        blog_content = self.llm.invoke(content_prompt).content.strip()

        return {
            "blog_title": blog_title,
            "blog_content": blog_content,
            "message": state["message"] + [
                SystemMessage(content="Transcript fetched successfully."),
                SystemMessage(content=f"Blog title generated: {blog_title}"),
                SystemMessage(content="Blog content generated successfully.")
            ]
        }
    def human_feedback(self, state: BlogGenState) -> BlogGenState:
        """Just an empty to update the feedback param"""
        return state