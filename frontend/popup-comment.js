function fetchCommentsFromBackground() {
  chrome.runtime.sendMessage({ action: "get_comments" }, function (response) {
    const container = document.getElementById("comments");

    if (!response || !response.comments) {
      container.innerHTML = "<p>❌ Could not load comments.</p>";
      return;
    }

    const comments = response.comments
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
