

document.addEventListener('DOMContentLoaded', function() {
  var playerForm = document.getElementById('player-form');
  playerForm.addEventListener('submit', handleFormSubmit);
});

function handleFormSubmit(event) {
  event.preventDefault(); // Prevent the default form submission

  handlePlayerSelection(); // Calls handlePlayerSelection function

}