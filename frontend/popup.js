console.log("📦 popup.js loaded");

chrome.storage.local.get(["savedPosts"], (result) => {
  const posts = result.savedPosts || [];
  const container = document.getElementById("posts");

  if (!posts.length) {
    container.innerText = "No saved posts yet.";
    return;
  }

  // Clear loading text
  container.innerHTML = "";

  posts.forEach(post => {
    const div = document.createElement("div");
    div.className = "post";
    div.style.marginBottom = "12px";
    div.innerHTML = `
      <strong>${post.author}</strong><br/>
      <small>${new Date(post.timestamp).toLocaleString()}</small>
      <p>${post.text.slice(0, 100)}${post.text.length > 100 ? "…" : ""}</p>
      ${post.image ? `<img src="${post.image}" style="max-width:100%;border-radius:4px"/>` : ""}
      <p><a href="${post.url}" target="_blank">🔗 View on LinkedIn</a></p>
      <hr/>
    `;
    container.appendChild(div);
  });
});
