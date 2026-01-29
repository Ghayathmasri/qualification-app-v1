// static/training.js
// FINAL – explicit session handoff via URL (no guessing)

document.addEventListener("DOMContentLoaded", async () => {

  const params = new URLSearchParams(window.location.search);
  const project = params.get("project");
  if (!project) {
    alert("Missing project");
    return;
  }

  const session_id = localStorage.getItem("session_id");
  if (!session_id) {
    alert("Missing session");
    return;
  }

  const res = await fetch(`/training?project=${encodeURIComponent(project)}`);
  if (!res.ok) {
    alert("Failed to load training");
    return;
  }

  const data = await res.json();

  document.getElementById("training-title").innerText = data.title || "";

  const rulesEl = document.getElementById("training-rules");
  rulesEl.innerHTML = "";
  (data.rules || []).forEach(r => {
    const li = document.createElement("li");
    li.innerText = r;
    rulesEl.appendChild(li);
  });

  const videosEl = document.getElementById("training-videos");
  videosEl.innerHTML = "";
  (data.videos || []).forEach(v => {
    const iframe = document.createElement("iframe");
    iframe.src = v;
    iframe.width = "560";
    iframe.height = "315";
    iframe.allowFullscreen = true;
    videosEl.appendChild(iframe);
  });

  document.getElementById("continue-btn").onclick = async () => {

    await fetch("/training_complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id })
    });

    // ✅ PASS SESSION EXPLICITLY
    window.location.href =
      `/static/quiz.html?project=${encodeURIComponent(project)}&session_id=${encodeURIComponent(session_id)}`;
  };
});
