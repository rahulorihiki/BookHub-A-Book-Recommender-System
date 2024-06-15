const searchInput = document.getElementById("searchInput");
const dropdown = document.getElementById("dropdown");

function filterFunction() {
  const text = searchInput.value.toLowerCase();
  dropdown.innerHTML = ""; // Clear previous dropdown items
  if (text) {
    fetch(`http://127.0.0.1:7000/api/books?search=${text}`) // Sends a GET request to Flask API
      .then((response) => response.json()) // Parses the JSON response
      .then((filteredBooks) => {
        if (filteredBooks.length > 0) {
          dropdown.style.display = "block"; // Show dropdown if items available
          filteredBooks.forEach((book) => {
            const div = document.createElement("div");
            div.textContent = book;
            div.onclick = function () {
              selectItem(book);
            };
            dropdown.appendChild(div);
          });
        } else {
          dropdown.style.display = "none"; // Hide dropdown if no items match
        }
      })
      .catch((error) => console.error("Error fetching data:", error));
  } else {
    dropdown.style.display = "none"; // Hide dropdown if input is empty
  }
}

function selectItem(value) {
  searchInput.value = value;
  dropdown.style.display = "none"; // Hide dropdown after selection
}

document.addEventListener("click", function (e) {
  if (e.target !== searchInput) {
    dropdown.style.display = "none"; // Hide dropdown when clicking outside
  }
});
