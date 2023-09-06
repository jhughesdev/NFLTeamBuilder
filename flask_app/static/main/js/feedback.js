var elem = document.getElementById("button1");
elem.addEventListener('click',toggleForm);

function toggleForm()
{
  var x = document.getElementById("form");
  if (x.style.visibility === "hidden")
  {
      x.style.visibility = "visible";
  }
  else
  {
      x.style.visibility = "hidden";
  }
}
