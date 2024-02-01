let loadButton = document.getElementById("loadMore");

loadButton.addEventListener("click", func1);
currentRoww = 2;
function func1() {
  roww = document.getElementsByClassName("roww");
  for (let index = currentRoww; index < currentRoww + 1; index++) {
    roww[index].style.display = "flex";
  }
  currentRoww += 1;

  if (currentRoww >= roww.length) {
    loadButton.style.display = "none";
  }
}

function standby() {
  console.log("It is reaching here bitch");
  document.getElementById("foo").src =
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQz9DTG5p3stAyHEndua38M7VoV-yFQKt6j8N-cf6v0gLg6U8WdS49Qdt0eb5Hmog7CGwU&usqp=CAU";
}
