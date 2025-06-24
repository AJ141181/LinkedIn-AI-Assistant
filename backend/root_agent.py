from typing import Dict
from google.adk.tools import BaseTool
from google.adk.agents import BaseAgent

from backend.agents.curator_agent import curator_agent
from backend.agents.summarizer_agent import summarizer_agent
from backend.agents.tagger_agent import tagger_agent
from backend.agents.comment_agent import comment_agent
from backend.agents.organizer_agent import organizer_agent


class LinkedInPipelineTool(BaseTool):
    name = "linkedin_pipeline_tool"
    description = "Curates, summarizes, tags, comments, and organizes a LinkedIn post using individual agents."

    def run(self, input_data: Dict, model=None) -> Dict:
        # Step 1: Curate
        curated = curator_agent.run(input_data)

        # Step 2: Summarize
        summary_result = summarizer_agent.run(curated)
        summary_text = summary_result.get("summary", "")

        # Step 3: Tag
        tags_text = tagger_agent.run({"summary": summary_text})

        # Step 4: Comment
        comment_result = comment_agent.run(curated)
        comments_text = comment_result.get("comments", "")

        # Step 5: Organize
        organizer_agent.run({
            "curated": curated,
            "summary": summary_text,
            "tags": tags_text
        })

        return {
            "curated": curated,
            "summary": summary_text,
            "tags": tags_text,
            "comments": comments_text,
            "status": "success"
        }
class RootAgent(BaseAgent):
    name: str = "root_agent"
    description: str = "Executes LinkedIn post pipeline using all tools."
    tools: list[BaseTool] = [
        LinkedInPipelineTool(
            name="linkedin_pipeline_tool",
            description="Curates, summarizes, tags, comments, and organizes a LinkedIn post."
        )
    ]

    def run(self, post_data: Dict) -> Dict:
        return self.tools[0].run(post_data)





# Export instance
root_agent = RootAgent()

