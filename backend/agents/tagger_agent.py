import logging
from typing import Dict
from google.adk.agents import LlmAgent
from backend.gemini_config import model  # ✅ Your Gemini model instance

# Logger setup
logger = logging.getLogger("TaggerAgent")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class TaggerAgent(LlmAgent):
    name : str = "tagger_agent"
    model: object = model

    def run(self, input_data: Dict) -> str:
        summary = str(input_data.get("summary", "")).strip()

        prompt = f"""You are an expert in content categorization. Based on the following summary, generate 5 relevant LinkedIn-style topic tags. Tags should be short, lowercase, and prefixed with '#'.

Summary:
{summary}

Output (5 tags):"""

        logger.info("Generating tags for summary: %s", summary[:100])
        response = self.model.generate_content(prompt)
        tags = response.text.strip()

        logger.info("Tags generated: %s", tags)
        return tags


# Exported instance
tagger_agent = TaggerAgent()

