$(document).ready(function () {
  function updateGame() {
    $.ajax({
      url: gameUrls.showGame,
      method: "GET",
      success: function (response) {
        $("body").html(response);
        var contentUpdatedEvent = new Event("contentUpdated");
        console.log("fart"); // Necessary functionality testing
        document.dispatchEvent(contentUpdatedEvent);
        updateCards(); // Dev. Console: Make sure this function updates UI elements correctly
      },
    });
  }

  // Bind actions to buttons
  $("#hit").click(function (event) {
    event.preventDefault();
    $.ajax({
      url: gameUrls.playerAction + "/hit",
      method: "GET",
      success: updateGame,
    });
  });

  $("#stay").click(function (event) {
    event.preventDefault();
    $.ajax({
      url: gameUrls.playerAction + "/stay",
      method: "GET",
      success: updateGame,
    });
  });

  $("#split").click(function (event) {
    event.preventDefault();
    $.ajax({
      url: gameUrls.playerAction + "/split",
      method: "GET",
      success: updateGame,
    });
  });

  $("#double").click(function (event) {
    event.preventDefault();
    $.ajax({
      url: gameUrls.playerAction + "/double_down",
      method: "GET",
      success: updateGame,
    });
  });

  $("#surrender").click(function (event) {
    event.preventDefault();
    $.ajax({
      url: gameUrls.playerAction + "/surrender",
      method: "GET",
      success: updateGame,
    });
  });

  $("#new-hand-button").click(function (event) {
    event.preventDefault();
    $.ajax({
      url: gameUrls.startNewHand,
      method: "POST",
      success: updateGame,
    });
  });

  $("#new-game-button").click(function (event) {
    event.preventDefault();
    $.ajax({
      url: gameUrls.startNewGame,
      method: "POST",
      success: updateGame,
    });
  });

  // for Developer Console function with jQuery AJAX
  $("#add-card-button").click(function (event) {
    event.preventDefault();
    var handType = $("#hand-type").val();
    var card = $("#card").val();
    $.ajax({
      url: "/game/add_card_to_hand",
      method: "POST",
      data: {
        hand_type: handType,
        card: card,
      },
      success: function (response) {
        $("body").html(response);
        console.log(response); // See what the server is actually returning
        updateGame(response);
      },
      error: function (xhr, status, error) {
        console.error("Error adding card:", error);
      },
    });
  });

  function updateCards() {
    // Ensure this updates your card displays after AJAX updates
    console.log("Cards updated");
  }
});
