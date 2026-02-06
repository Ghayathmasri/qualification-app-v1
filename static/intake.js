document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("intake-form");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const params = new URLSearchParams(window.location.search);
    const project = params.get("project");
    if (!project) {
      alert("Missing project");
      return;
    }

    const payload = {
      name: document.getElementById("name").value,
      email: document.getElementById("email").value,
      country: document.getElementById("country").value,
      age_group: document.getElementById("age_group").value,
      native_language: document.getElementById("native_language").value,
      academic_level: document.getElementById("academic_level").value,
      qualifications: document.getElementById("qualifications").value,
      language_proficiency: []
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

    // 🔒 SINGLE SOURCE OF TRUTH
    localStorage.setItem("session_id", data.session_id);

    // 🔒 PASS SESSION EXPLICITLY
    window.location.href =
      `/static/training.html?project=${project}&session_id=${data.session_id}`;
  });
});
