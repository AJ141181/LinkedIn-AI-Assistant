
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.root_agent import root_agent 
from backend.agents.comment_agent import comment_agent  
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains during development


@app.route('/')
def health_check():
    return "✅ LinkedIn Agent Backend is running", 200


@app.route('/save-post', methods=['POST'])
def save_post():
    try:
        post_data = request.get_json()
        print("📥 Received Post Data:", post_data)

        # 🚀 Call root orchestrator agent to process post data
        #result = asyncio.run(linkedin_orchestrator.arun(post_data))
        # result = linkedin_orchestrator.run(post_data)
        #result = linkedin_orchestrator(post_data)
        #result = asyncio.run(root_agent.arun(post_data))
        result = root_agent(post_data)
        

        print("✅ Orchestration Result:", result)
        return jsonify({"status": "success", "result": result}), 200

    except Exception as e:
        print("❌ Error in /save-post:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/generate-comments', methods=['POST'])
def generate_comments():
    try:
        post_data = request.get_json()
        print("🗨️ Received Post for Comment Generation:", post_data)

        # Run Comment Agent
        result = comment_agent.run(post_data)

        print("✅ Comment Suggestions:", result)
        return jsonify(result), 200

    except Exception as e:
        print("❌ Error in /generate-comments:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)  # Local HTTPS for extension compatibility
