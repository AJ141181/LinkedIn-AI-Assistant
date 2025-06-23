from google.adk.agents import BaseAgent
from google.adk.tools import BaseTool
from typing import List


class CuratePostTool(BaseTool):
    def run(self, input_data: dict) -> dict:
        return {
            "author": str(input_data.get("author", "Unknown")),
            "likes": input_data.get("likes", 0),
            "comments": input_data.get("comments", 0),
            "reposts": input_data.get("reposts", 0),
            "timestamp": input_data.get("timestamp", "N/A"),
            "text": str(input_data.get("text", "")),  # ✅ type-safe
            "post_information": str(input_data.get("post_information", "")),  # ✅ type-safe
            "images": input_data.get("images", []),
            "videos": input_data.get("videos", []),
            "documents": input_data.get("documents", []),
            "url": input_data.get("url", ""),
            "followers": input_data.get("followers", ""),
            "newsletter": input_data.get("newsletter", ""),
            "webpage": input_data.get("webpage", "")
        }


class CuratorAgent(BaseAgent):
    tools: List[BaseTool] = [
        CuratePostTool(
            name="curate_post_tool",
            description="Extracts and structures metadata from LinkedIn posts including media, documents, and extended info."
        )
    ]

    def run(self, input_data: dict):
        return self.tools[0].run(input_data)


curator_agent = CuratorAgent(name="curator_agent")
