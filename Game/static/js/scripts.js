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
    const suits = ["Hearts", "Diamonds", "Clubs", "Spades"];
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

    const cardWidth = 150;
    const cardHeight = 210;
    const svgUrl = "https://assets.codepen.io/67732/card-faces.svg";

    container.innerHTML = ""; // Clear previous content
    const div = document.createElement("div");
    div.classList.add("card");
    div.style.backgroundImage = `url('${svgUrl}')`;
    div.style.backgroundSize = `${cardWidth * ranks.length}px ${
      cardHeight * suits.length
    }px`;
    cardId = cardId.trim();
    const [rank, suit] = parseCardId(cardId);
    const suitIndex = suits.indexOf(suit);
    const rankIndex = ranks.indexOf(rank);

    // Calculate the correct position to display the card
    const posX = rankIndex * cardWidth;
    const posY = suitIndex * cardHeight;
    div.style.backgroundPosition = `-${posX}px -${posY}px`;

    // Center the card within the container
    div.style.display = "block";
    div.style.margin = "auto";

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
        document.querySelector(".player-cards").innerHTML =
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
