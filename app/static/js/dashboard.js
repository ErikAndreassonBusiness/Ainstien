// app/static/js/dashboard.js
document.addEventListener("DOMContentLoaded", function () {
  const rows = document.querySelectorAll(".stock-row");

  rows.forEach((row) => {
    row.addEventListener("click", function (e) {
      // Don't trigger if clicking a specific link or button inside the row
      if (e.target.tagName === "A" || e.target.tagName === "BUTTON") {
        return;
      }

      const url = this.getAttribute("data-url");
      if (url) {
        window.location.href = url;
      }
    });
  });
  console.log("Dashboard: Table row listeners active.");
});
