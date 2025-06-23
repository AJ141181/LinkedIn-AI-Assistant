function fetchCommentsFromCloudRun(postText) {
  const container = document.getElementById("comments");
  container.innerHTML = "<p>⏳ Generating comments...</p>";

  fetch("https://linkedin-curator-198258385336.us-central1.run.app/generate-comments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ text: postText })
  })
    .then(res => res.json())
    .then(data => {
      const comments = data.comments
        .split("\n")
        .filter(line => line.trim().startsWith("- Comment"))
        .map(c => c.replace(/^- Comment \d+?:?\s*/, "").trim());

      container.innerHTML = "";
      comments.forEach((commentText, index) => {
        const div = document.createElement("div");
        div.className = "comment-option";

        const textarea = document.createElement("textarea");
        textarea.id = `comment-${index}`;
        textarea.value = commentText;

        const button = document.createElement("button");
        button.innerText = "Post This";
        button.addEventListener("click", () => postToLinkedIn(textarea.value));

        div.appendChild(textarea);
        div.appendChild(button);
        container.appendChild(div);
      });
    })
    .catch(err => {
      console.error("❌ Comment fetch error:", err);
      container.innerHTML = "<p>❌ Failed to generate comments.</p>";
    });
}

function fetchCommentsFromBackground() {
  chrome.runtime.sendMessage({ action: "get_post_data" }, function (response) {
    if (!response || !response.text) {
      const container = document.getElementById("comments");
      container.innerHTML = "<p>❌ Could not load post data.</p>";
      return;
    }

    fetchCommentsFromCloudRun(response.text);
  });
}

function postToLinkedIn(text) {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.runtime.sendMessage({
      action: "inject_comment",
      comment: text,
      tabId: tabs[0].id
    });
  });
}

document.addEventListener("DOMContentLoaded", fetchCommentsFromBackground);
