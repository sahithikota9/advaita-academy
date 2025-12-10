// main.js - handles modal and add exam interaction
document.addEventListener("DOMContentLoaded", () => {
  const addBtn = document.getElementById("addExamBtn");
  const modal = document.getElementById("modal");
  const cancelBtn = document.getElementById("cancelBtn");
  const form = document.getElementById("addExamForm");
  const examList = document.getElementById("exam-list");

  function openModal(){
    modal.classList.remove("hidden");
  }
  function closeModal(){
    modal.classList.add("hidden");
  }

  addBtn && addBtn.addEventListener("click", openModal);
  cancelBtn && cancelBtn.addEventListener("click", closeModal);

  form && form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const exam_name = document.getElementById("exam_name").value || "Exam";
    const math = parseInt(document.getElementById("math").value||0);
    const physics = parseInt(document.getElementById("physics").value||0);
    const chemistry = parseInt(document.getElementById("chemistry").value||0);

    const payload = { exam_name, math, physics, chemistry };
    try {
      const res = await fetch("/add_score", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success){
        // prepend new exam card to list
        const e = data.exam;
        const html = buildExamHTML(e);
        // Insert at top:
        if (examList.firstChild && examList.querySelector('.muted')){
          // remove "no exam" message if present
          examList.innerHTML = html + examList.innerHTML;
        } else {
          examList.insertAdjacentHTML('afterbegin', html);
        }
        closeModal();
        form.reset();
      } else {
        alert(data.error || "Failed");
      }
    } catch(err){
      alert("Network error: " + err.message);
    }
  });

  function buildExamHTML(e){
    const date = e.date ? e.date.replace('T',' ').slice(0,19) : "";
    return `
      <article class="result-card">
        <div class="result-head">
          <div class="exam-name">${escapeHtml(e.exam_name)}</div>
          <div class="exam-date">${escapeHtml(date)}</div>
        </div>
        <table class="marks-table">
          <thead><tr><th>Subject</th><th>Marks</th></tr></thead>
          <tbody>
            <tr><td>Math</td><td>${e.math}</td></tr>
            <tr><td>Physics</td><td>${e.physics}</td></tr>
            <tr><td>Chemistry</td><td>${e.chemistry}</td></tr>
          </tbody>
          <tfoot><tr><th>Total</th><th>${e.total}</th></tr></tfoot>
        </table>
      </article>
    `;
  }

  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, function(m){ return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"})[m]; }); }
});
