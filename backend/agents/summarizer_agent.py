import logging
from typing import Dict
from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from backend.gemini_config import model  # Your Gemini model instance

# Logger setup
logger = logging.getLogger("SummarizerAgent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s"))
logger.addHandler(handler)


class SummarizePostTool(BaseTool):
    name = "summarize_post_tool"
    description = "Summarizes professional LinkedIn posts for business reporting."

    def run(self, input_data: Dict, model = None) -> Dict:
        post_text = input_data.get("text", "")
        post_context = input_data.get("post_information", "")

        if not isinstance(post_text, str):
            raise TypeError("Expected 'text' to be a string")
        if not isinstance(post_context, str):
            raise TypeError("Expected 'post_information' to be a string")

        post_text = post_text.strip()
        post_context = post_context.strip()
        post_context_block = f"Additional Context:\n{post_context}\n\n" if post_context else ""

        prompt = (
            "You are an AI summarization assistant trained to analyze professional LinkedIn posts.\n"
            "Summarize the content below in a concise paragraph for business reporting.\n\n"
            f"Post Content:\n{post_text}\n\n{post_context_block}Summary:"
        )

        logger.info("Post text for summarization: %s", post_text[:100])
        response = model.generate_content(prompt)
        summary = response.text.strip()

        return {"status": "success", "summary": summary}


# 🎯 LlmAgent version
class SummarizerAgent(LlmAgent):
    name: str = "summarizer_agent"
    model: object = model
    tools: list = [SummarizePostTool(name="summarize_post_tool",
            description="Summarizes professional LinkedIn posts for business reporting."
        )
    ]

    def run(self, input_data: Dict):
        return self.tools[0].run(input_data, model=self.model)


# Export instance
summarizer_agent = SummarizerAgent()

