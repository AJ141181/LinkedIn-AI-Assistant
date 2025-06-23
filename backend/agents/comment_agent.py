import logging
from typing import Dict
from google.adk.agents import LlmAgent
from backend.gemini_config import model  # Gemini Pro model instance

# Logger setup
logger = logging.getLogger("CommentAgent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class CommentAgent(LlmAgent):
    name: str = "comment_agent"
    model: object = model

    def __init__(self):
        super().__init__() # Call the parent class constructor

        self.model = model
        self.name = "comment_agent"

    def run(self, input_data: Dict) -> Dict:
        try:
            post_text = str(input_data.get("text", "")).strip()
            post_context = str(input_data.get("post_information", "")).strip()

            logger.info("Generating comments for post.")

            prompt = f"""
You are an AI assistant that reads professional LinkedIn posts and helps users craft thoughtful, concise comments.

Post Content:
{post_text}

{f"Additional Context:\n{post_context}" if post_context else ""}

Now based on the tone, emotion, and topic of the post, write 3 distinct and meaningful comments that are helpful, relevant, and under 100 words each.

Format:
- Comment 1: ...
- Comment 2: ...
- Comment 3: ...
"""

            response = self.model.generate_content(prompt)
            comments = response.text.strip()

            logger.info("Comments generated successfully.")
            return {
                "status": "success",
                "comments": comments
            }

        except Exception as e:
            logger.exception("CommentAgent failed")
            return {
                "status": "error",
                "comments": None,
                "error": str(e)
            }


# Export instance
comment_agent = CommentAgent()



