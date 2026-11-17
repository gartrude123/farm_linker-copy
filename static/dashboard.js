// static/dashboard.js
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

});
