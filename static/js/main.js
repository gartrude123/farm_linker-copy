// FARM_LINKER - Main JavaScript
document.addEventListener("DOMContentLoaded", () => {

  // ---- Dismiss flash messages ----
  document.querySelectorAll(".flash-dismiss").forEach(btn => {
    btn.addEventListener("click", () => {
      const flash = btn.closest(".flash");
      if (flash) flash.style.display = "none";
    });
  });

  // Auto-dismiss flashes after 7 seconds
  setTimeout(() => {
    document.querySelectorAll(".flash").forEach(f => { f.style.display = "none"; });
  }, 7000);

  // ---- Toggle mobile nav ----
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => links.classList.toggle("open"));
    links.querySelectorAll("a").forEach(a => a.addEventListener("click", () => links.classList.remove("open")));
  }

  // ---- Generic modal helpers ----
  window.openModal = function(id) {
    const m = document.getElementById(id);
    if (m) m.classList.add("show");
  };

  window.closeModal = function(id) {
    const m = document.getElementById(id);
    if (m) m.classList.remove("show");
  };

  // Close modal on backdrop click
  document.querySelectorAll(".modal").forEach(m => {
    m.addEventListener("click", e => { if (e.target === m) m.classList.remove("show"); });
  });

  // ---- AJAX form submissions (generic) ----
  document.querySelectorAll("form.ajax-form").forEach(form => {
    form.addEventListener("submit", async e => {
      e.preventDefault();
      const btn = form.querySelector("button[type='submit']");
      const originalText = btn.innerHTML;
      btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Saving...';
      btn.disabled = true;

      const formData = new FormData(form);
      try {
        const res = await fetch(form.action, {
          method: form.method,
          body: formData,
        });
        if (res.ok || res.redirected) {
          if (res.redirected) window.location.href = res.url;
          else location.reload();
        } else {
          const text = await res.text();
          alert("Save failed: " + text);
        }
      } catch (err) {
        alert("Network error: " + err.message);
      } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
      }
    });
  });

  // ---- Delete confirm buttons ----
  document.querySelectorAll(".deleteBtn").forEach(btn => {
    btn.addEventListener("click", e => {
      if (!confirm("Are you sure you want to delete this record?")) {
        e.preventDefault();
        return false;
      }
    });
  });

  // ---- Order status badge color ----
  document.querySelectorAll(".badge").forEach(b => {
    const cls = b.className;
    if (cls.includes("Completed")) b.style.background = "#bbf7d0";
    if (cls.includes("Delivered")) b.style.background = "#d1fae5";
    if (cls.includes("In Transit")) b.style.background = "#e0e7ff";
    if (cls.includes("Approved")) b.style.background = "#dbeafe";
    if (cls.includes("Pending")) b.style.background = "#fef3c7";
    if (cls.includes("Rejected")) b.style.background = "#fee2e2";
    if (cls.includes("Paid")) b.style.background = "#d1fae5";
    if (cls.includes("Unpaid")) b.style.background = "#fee2e2";
  });

});
