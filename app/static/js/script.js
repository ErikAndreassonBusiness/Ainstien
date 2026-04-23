document.addEventListener("DOMContentLoaded", function () {
  // Select all rows with the class 'stock-row'
  const rows = document.querySelectorAll(".stock-row");

  rows.forEach((row) => {
    row.addEventListener("click", function (e) {
      // Check if the click was on the button itself or a link
      // If it was, let the browser handle it normally.
      if (e.target.tagName === "A" || e.target.tagName === "BUTTON") {
        return;
      }

      // Otherwise, get the URL from the data attribute and navigate
      const url = this.getAttribute("data-url");
      if (url) {
        window.location.href = url;
      }
    });
  });
});
