
from backend.agents.curator_agent import curator_agent
from backend.agents.summarizer_agent import summarizer_agent
from backend.agents.tagger_agent import tagger_agent
from backend.agents.comment_agent import comment_agent
from backend.agents.organizer_agent import organizer_agent

def run_pipeline(post_data: dict):
    # Step 1: Curate
    curated = curator_agent.run(post_data)

    # Step 2: Summarize
    summary_result = summarizer_agent.run(curated)
    summary_text = summary_result.get("summary", "")


    # Step 3: Generate tags
    tags_text = tagger_agent.run({"summary": summary_text})

    # Step 4: Generate comment suggestions from post
    comment_result = comment_agent.run(curated)
    comments_text = comment_result.get("comments", "")

    # Step 5: Save post summary and tags to Google Sheets
    organizer_agent.run({
        "curated": curated,
        "summary": summary_text,
        "tags": tags_text

    
    })

    return {
        "curated": curated,
        "summary": summary_text,
        "tags": tags_text,
        "comments": comments_text
    }
root_agent = run_pipeline

