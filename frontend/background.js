let latestPostData = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "save_post_data") {
    latestPostData = request.data;
    console.log("📥 Post data saved in background:", latestPostData);
    sendResponse({ status: "saved" });
  }

  if (request.action === "get_comments") {
    if (!latestPostData) {
      sendResponse({ error: "No post data available." });
      return;
    }

    console.log("🧠 Fetching comment suggestions for:", latestPostData);

    fetch("http://localhost:5000/generate-comments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(latestPostData),
    })
      .then(res => res.json())
      .then(data => {
        console.log("✅ Comments received:", data);
        sendResponse({ comments: data.comments });
      })
      .catch(err => {
        console.error("❌ Error fetching comments:", err);
        sendResponse({ error: err.toString() });
      });

    return true; // Keeps message channel open for async response
  }
  if (request.action === "inject_comment") {
    const tabId = request.tabId || sender.tab?.id;
    
   chrome.scripting.executeScript({
  target: { tabId: tabId },
  func: (commentText) => {
    const targetPost = document.querySelector('[data-ai-curator-comment-target="true"]');
    if (!targetPost) {
      alert("⚠️ Could not find the correct post. Please re-click 'Post Comment' on the post.");
      return;
    }

    const commentBox = targetPost.querySelector('div[role="textbox"]');
    if (commentBox) {
      commentBox.focus();
      document.execCommand("insertText", false, commentText);
    } else {
      alert("⚠️ Comment box not found. Please click 'Comment' on the post manually before hitting 'Post This'.");
    }

    // Clean up marker
    targetPost.removeAttribute("data-ai-curator-comment-target");
  },
  args: [request.comment]
});
 
}

});
