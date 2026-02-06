document.addEventListener("DOMContentLoaded", async () => {
  const params = new URLSearchParams(window.location.search);
  const project = params.get("project");
  const session_id =
    params.get("session_id") || localStorage.getItem("session_id");

  if (!project || !session_id) {
    alert("Missing project or session");
    return;
  }

  // 🔒 RE-PERSIST SESSION
  localStorage.setItem("session_id", session_id);

  const continueBtn = document.getElementById("continue-btn");
  continueBtn.disabled = true;
  continueBtn.type = "button";

  // =========================
  // Load training config
  // =========================
  const res = await fetch(`/training?project=${project}`);
  if (!res.ok) {
    alert("Failed to load training");
    return;
  }

  const data = await res.json();

  // =========================
  // Title
  // =========================
  document.getElementById("title").innerText = data.title || "";

  // =========================
  // Rules
  // =========================
  const rulesEl = document.getElementById("rules");
  rulesEl.innerHTML = "";
  (data.rules || []).forEach(r => {
    const li = document.createElement("li");
    li.textContent = r;
    rulesEl.appendChild(li);
  });

  // =========================
  // Materials
  // =========================
  const materialsEl = document.getElementById("materials");
  materialsEl.innerHTML = "";

  const completed = new Set();
  const materials = data.materials || [];

  materials.forEach((m, idx) => {
    const row = document.createElement("div");
    row.className = "material";

    const link = document.createElement("a");
    link.href = m.file;
    link.target = "_blank";
    link.textContent = m.label;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "Mark Completed";
    btn.style.marginLeft = "10px";

    btn.onclick = () => {
      completed.add(idx);
      btn.disabled = true;
      checkReady();
    };

    row.appendChild(link);
    row.appendChild(btn);
    materialsEl.appendChild(row);
  });

  // =========================
  // Video
  // =========================
  const videoContainer = document.getElementById("video-container");
  videoContainer.innerHTML = "";

  const video = document.createElement("video");
  video.src = data.video;
  video.controls = true;
  video.style.width = "100%";

  videoContainer.appendChild(video);
  video.addEventListener("ended", checkReady);

  function checkReady() {
    const docsDone = completed.size === materials.length;
    const videoDone = video.ended === true;

    if (docsDone && videoDone) {
      continueBtn.disabled = false;
    }
  }

  // =========================
  // Continue → Quiz
  // =========================
  continueBtn.onclick = async () => {
    const r = await fetch("/training_complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id })
    });

    if (!r.ok) {
      alert("Failed to continue");
      return;
    }

    // 🔒 PASS SESSION AGAIN
    window.location.href =
      `/static/quiz.html?project=${project}&session_id=${session_id}`;
  };
});
