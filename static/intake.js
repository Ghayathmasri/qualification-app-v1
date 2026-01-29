// static/intake.js
// FIXED: session_id persistence for quiz & training

document.addEventListener("DOMContentLoaded", () => {

  const form = document.getElementById("intake-form");
  const addBtn = document.getElementById("add-lang-btn");

  addBtn.addEventListener("click", addLanguage);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const params = new URLSearchParams(window.location.search);
    const project = params.get("project");
    if (!project) {
      alert("Missing project");
      return;
    }

    const language_proficiency = [];
    document.querySelectorAll(".lang-row").forEach(row => {
      language_proficiency.push({
        language: row.querySelector(".lang-name").value,
        reading: row.querySelector(".lang-reading").value,
        writing: row.querySelector(".lang-writing").value,
        listening: row.querySelector(".lang-listening").value,
        speaking: row.querySelector(".lang-speaking").value
      });
    });

    const payload = {
      name: document.getElementById("name").value,
      email: document.getElementById("email").value,
      country: document.getElementById("country").value,
      age_group: document.getElementById("age_group").value,
      native_language: document.getElementById("native_language").value,
      academic_level: document.getElementById("academic_level").value,
      qualifications: document.getElementById("qualifications").value,
      language_proficiency
    };

    const res = await fetch(`/start?project=${project}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      alert("Failed to start qualification");
      return;
    }

    const data = await res.json();

    // ✅ CRITICAL FIX
    localStorage.setItem("session_id", data.session_id);

    window.location.href = `/static/training.html?project=${project}`;
  });
});

function addLanguage() {
  const box = document.getElementById("languages");

  const row = document.createElement("div");
  row.className = "lang-row";

  row.innerHTML = `
    <input class="lang-name" placeholder="Language">
    <input class="lang-reading" placeholder="Reading">
    <input class="lang-writing" placeholder="Writing">
    <input class="lang-listening" placeholder="Listening">
    <input class="lang-speaking" placeholder="Speaking">
    <hr>
  `;

  box.appendChild(row);
}
