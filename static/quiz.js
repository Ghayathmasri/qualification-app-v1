// static/quiz.js
// FINAL – deterministic session handling (no storage dependency)

document.addEventListener("DOMContentLoaded", async () => {

  const params = new URLSearchParams(window.location.search);
  const project = params.get("project");
  const session_id = params.get("session_id");

  if (!project || !session_id) {
    alert("Missing project or session");
    return;
  }

  // Load quiz
  const res = await fetch("/quiz", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id })
  });

  if (!res.ok) {
    alert("Quiz not available");
    return;
  }

  const data = await res.json();
  const container = document.getElementById("questions");

  if (!data.questions || data.questions.length === 0) {
    container.innerText = "No quiz required.";
    return;
  }

  // Render questions
  data.questions.forEach(q => {
    const div = document.createElement("div");
    div.innerHTML = `<p>${q.question}</p>`;

    q.options.forEach(opt => {
      const label = document.createElement("label");
      label.innerHTML = `
        <input type="radio" name="${q.id}" value="${opt}">
        ${opt}
      `;
      div.appendChild(label);
      div.appendChild(document.createElement("br"));
    });

    container.appendChild(div);
  });

  // Submit quiz
  document.getElementById("quiz-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const answers = {};
    data.questions.forEach(q => {
      const selected = document.querySelector(`input[name="${q.id}"]:checked`);
      if (selected) answers[q.id] = selected.value;
    });

    const submitRes = await fetch("/submit_mcq", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, answers })
    });

    if (!submitRes.ok) {
      alert("Failed to submit quiz");
      return;
    }

    window.location.href =
      `/static/transcription.html?project=${encodeURIComponent(project)}&session_id=${encodeURIComponent(session_id)}`;
  });

});
