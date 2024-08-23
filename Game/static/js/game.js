$(document).ready(function () {
  function updateGame() {
    $.ajax({
      url: gameUrls.showGame,
      method: "GET",
      success: function (response) {
        $("body").html(response);
        var contentUpdatedEvent = new Event("contentUpdated");
        console.log("fart");
        document.dispatchEvent(contentUpdatedEvent);
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
});
