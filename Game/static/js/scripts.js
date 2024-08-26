document.addEventListener("DOMContentLoaded", function () {
  // Initialize cards on page load
  $(document).on("contentUpdated", function () {
    updateCards(); // Call updateCards when the custom event is triggered
  });

  updateCards();

  // Add event listeners to action buttons (e.g., Hit, Stay, etc.)
  document.body.addEventListener("click", function (e) {
    if (e.target.matches(".action-button")) {
      e.preventDefault();
      const action = e.target.getAttribute("data-action");
      sendActionRequest(action);
    }
  });
  document.addEventListener("name-of-event", function (e) {
    console.log(e.detail); // Prints "Example of an event"
  });

  function updateCards() {
    const cardContainers = document.querySelectorAll("[data-card-id]"); // Select all elements with data-card-id attribute

    cardContainers.forEach(function (cardContainer) {
      const cardId = cardContainer.dataset.cardId; // Get card ID from data attribute
      displayCard(cardId, cardContainer); // Call display function with the card ID and the respective container
    });
  }

  function displayCard(cardId, container) {
    const suits = ["Spades", "Hearts", "Diamonds", "Clubs"];
    const ranks = [
      "A",
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
      "10",
      "J",
      "Q",
      "K",
    ];

    // Desired card size
    const cardWidth = 150; // Adjust to your desired card width
    const cardHeight = 210; // Adjust to your desired card height
    const svgUrl = "https://assets.codepen.io/67732/card-faces.svg";

    container.innerHTML = ""; // Clear previous content
    const div = document.createElement("div");
    div.classList.add("card");
    div.style.position = "absolute";
    //div.style.width = "100%";
    //div.style.height = "100%";
    div.style.backgroundImage = `url('${svgUrl}')`;
    div.style.backgroundSize = "auto 400%"; // Keep width auto, scale height to 400%
    div.style.backgroundRepeat = "no-repeat";

    // Trim any spaces from cardId before processing
    cardId = cardId.trim();

    const [rank, suit] = parseCardId(cardId);
    const suitIndex = suits.indexOf(suit);
    const rankIndex = ranks.indexOf(rank);

    // Calculate background position using similar logic to CSS
    const backgroundPositionX = (rankIndex * 100) / (ranks.length - 1); // Adjust the rank position
    const backgroundPositionY = (suitIndex * 100) / (suits.length - 1); // Adjust the suit position

    div.style.backgroundPosition = `${backgroundPositionX}% ${backgroundPositionY}%`;

    container.appendChild(div);
  }

  function parseCardId(cardId) {
    const parts = cardId.split(" of ");
    return [parts[0], parts[1]];
  }

  function sendActionRequest(action) {
    fetch(`/game/player_action/${action}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        // Update HTML content
        document.querySelector(".player-hands").innerHTML =
          data.player_hands_html;
        document.querySelector(".dealer-hand").innerHTML =
          data.dealer_hand_html;
        document.querySelector(
          ".chips"
        ).innerHTML = `Bankroll: $${data.bankroll} <p id="current-bet">Current Bet: $${data.bet}</p>`;

        // Reinitialize card rendering and other functionalities
        updateCards();
      })

      .catch((error) => console.error("Error:", error));
  }
});
function updateGame() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", gameUrls.showGame, true);
  xhr.onload = function () {
    if (xhr.status === 200) {
      document.getElementById("container-game").innerHTML = xhr.responseText;
      // Create and dispatch the custom event
      var event = new Event("contentUpdated");
      document.dispatchEvent(event);
    }
  };
  xhr.send();
}