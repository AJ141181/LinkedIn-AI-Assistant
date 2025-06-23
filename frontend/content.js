console.log("👀 content.js running...");

function extractPostData(postElement) {
  const text = postElement.innerText || "";
  const images = Array.from(postElement.querySelectorAll("img")).map(img => img.src);
  const author = postElement.querySelector("span[dir='ltr']")?.innerText || "Unknown";

  // ✅ Robust Likes, Comments, Reposts extraction
    let likes = "0", comments = "0", reposts = "0";

  // ✅ Primary likes method (your original logic)
  const likesEl = postElement.querySelector(
    "span.social-details-social-counts__reactions-count, span[aria-label*='like'], span[aria-label*='reaction']"
);
  if (likesEl && likesEl.innerText.match(/\d[\d,]*/)) {
    likes = likesEl.innerText.match(/\d[\d,]*/)[0].replace(/,/g, "");
}

  // ✅ Fallback for visually grouped spans (e.g. just "1,907" next to like icons)
  if (likes === "0") {
    const numericSpan = Array.from(postElement.querySelectorAll("span"))
      .find(span => /^\d[\d,]*$/.test(span.innerText.trim()));
    if (numericSpan) {
      likes = numericSpan.innerText.trim().replace(/,/g, "");
    }
}

  // ✅ Your working logic for comments & reposts
  const spans = Array.from(postElement.querySelectorAll("span"));
  spans.forEach(span => {
    const txt = span.innerText.toLowerCase();

    if (txt.includes("comment")) {
      const match = txt.match(/(\d[\d,]*)/);
      if (match) comments = match[1].replace(/,/g, "");
  }

    if (txt.includes("repost") || txt.includes("share")) {
      const match = txt.match(/(\d[\d,]*)/);
      if (match) reposts = match[1].replace(/,/g, "");
  }
});

  

  // ✅ Followers
  let followers = "";
  spans.forEach(span => {
    const match = span.innerText.match(/(\d[\d,]*)\s+followers/i);
    if (match) followers = match[1].replace(/,/g, "");
  });

  // ✅ Newsletter / Portfolio links
  const linkTexts = Array.from(postElement.querySelectorAll("a"))
    .map(a => a.href)
    .filter(href =>
      href &&
      !href.includes("linkedin.com/feed/") &&
      !href.includes("#") &&
      !href.includes("/posts/") &&
      !href.includes("javascript:void")
    );
  const newsletter = linkTexts.join(", ");

  // ✅ Construct clean URL from URN
  const urn = postElement.getAttribute("data-urn");
  let url = window.location.href;
  if (urn) {
    url = `https://www.linkedin.com/feed/update/${urn.replace(/:/g, "%3A")}`;
  }

  // ✅ Clean timestamp
  const timestamp = new Date().toISOString().split(".")[0].replace("T", " ");

  return {
    text,
    author,
    timestamp,
    likes,
    comments,
    reposts,
    url,
    images,
    videos: [],
    mediaLinks: [],
    post_information: text,
    followers,
    newsletter,
    additionalInfo: {
      followers,
      newsletter,
      richPreview: ""
    }
  };
}

function showFeedback(element, message, isError = false) {
  element.textContent = message;
  element.style.color = isError ? "red" : "green";
  setTimeout(() => {
    element.textContent = "";
  }, 3000);
}

function injectButtons(postElement) {
  console.log("🔧 Attempting to inject buttons into post");

  if (postElement.querySelector(".ai-curator-buttons")) {
    console.log("⏩ Buttons already injected, skipping.");
    return;
  }

  const actionBar = postElement.querySelector("div.feed-shared-social-action-bar, footer");
  if (!actionBar) {
    console.log("❌ No social-actions area found. HTML preview:", postElement.innerHTML.slice(0, 500));
    return;
  }

  const container = document.createElement("div");
  container.className = "ai-curator-buttons";
  container.style.display = "flex";
  container.style.gap = "8px";
  container.style.marginTop = "6px";

  const feedbackMsg = document.createElement("span");
  feedbackMsg.style.marginLeft = "10px";
  feedbackMsg.style.fontSize = "12px";
  feedbackMsg.style.color = "green";

  // 🔖 Save Post Button
  const saveBtn = document.createElement("button");
  saveBtn.innerText = "🔖 Save Post";
  saveBtn.style.cursor = "pointer";
  saveBtn.onclick = () => {
    const postData = extractPostData(postElement);
    console.log("📤 Sending post data:", postData);
    feedbackMsg.textContent = "💾 Saving post…";
    feedbackMsg.style.color = "blue";

    fetch("https://linkedin-curator-198258385336.us-central1.run.app/save-post"
, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(postData)
    })
      .then(res => res.json())
      .then(data => {
        console.log("✅ Post saved:", data);
        showFeedback(feedbackMsg, "✅ Post saved!");
      })
      .catch(err => {
        console.error("❌ Save error:", err);
        showFeedback(feedbackMsg, "❌ Save failed", true);
      });
  };

  // 💬 Post Comment Button
  const commentBtn = document.createElement("button");
  commentBtn.innerText = "💬 Post Comment";
  commentBtn.style.cursor = "pointer";

  commentBtn.onclick = () => {
    const postData = extractPostData(postElement);
    document.querySelectorAll('[data-ai-curator-comment-target]').forEach(el =>
      el.removeAttribute('data-ai-curator-comment-target')
  );

  // Tag this post for comment injection
    postElement.setAttribute("data-ai-curator-comment-target", "true");


    chrome.runtime.sendMessage({ action: "save_post_data", data: postData });
    showFeedback(feedbackMsg, "💡 Post ready — click the extension icon to see comments");
  };

  container.appendChild(saveBtn);
  container.appendChild(commentBtn);
  container.appendChild(feedbackMsg);
  actionBar.appendChild(container);
}

function scanAndInject() {
  console.log("🔄 scanAndInject running...");

  const posts = document.querySelectorAll("div.feed-shared-update-v2, div[data-urn^='urn:li:activity']");
  console.log("🧱 Found", posts.length, "post blocks");

  posts.forEach((post, i) => {
    console.log(`📦 Post ${i + 1}:`, post);
    injectButtons(post);
  });
}

// Run every 1.5 seconds to catch new posts
setInterval(scanAndInject, 1500);
