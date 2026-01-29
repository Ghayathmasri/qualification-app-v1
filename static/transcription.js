/**
 * Transcription Page Logic
 * - Loads transcription tasks
 * - Plays local audio
 * - Collects user transcriptions
 * - Submits results
 */

document.addEventListener("DOMContentLoaded", async () => {

  const params = new URLSearchParams(window.location.search);
  const project = params.get("project");
  const session_id = localStorage.getItem("session_id");

  if (!project || !session_id) {
    alert("Missing project or session");
    return;
  }

  // Load transcription tasks
  const res = await fetch("/transcription_task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id })
  });

  if (!res.ok) {
    alert("Transcription not available");
    return;
  }

  const data = await res.json();
  const container = document.getElementById("tasks");

  if (!data.tasks || data.tasks.length === 0) {
    container.innerText = "No transcription required.";
    return;
  }

  // Render tasks
  data.tasks.forEach(task => {
    const div = document.createElement("div");

    div.innerHTML = `
      <audio controls src="${task.audio_url}"></audio><br>
      <textarea rows="4" cols="80" data-task="${task.task_id}" placeholder="Type what you hear"></textarea>
      <hr>
    `;

    container.appendChild(div);
  });

  // Submit transcriptions
  document.getElementById("submit-btn").addEventListener("click", async () => {

    const textareas = document.querySelectorAll("textarea");
    for (const ta of textareas) {
      if (!ta.value.trim()) {
        alert("Please complete all transcriptions");
        return;
      }
    }

    for (const ta of textareas) {
      await fetch("/submit_transcription", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id,
          task_id: ta.dataset.task,
          transcription: ta.value
        })
      });
    }

    window.location.href = "/static/done.html";
  });

});
