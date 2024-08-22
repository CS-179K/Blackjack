document.addEventListener("DOMContentLoaded", function () {
  const cardContainers = document.querySelectorAll("[data-card-id]"); // Select all elements with data-card-id attribute

  cardContainers.forEach(function (cardContainer) {
    const cardId = cardContainer.dataset.cardId; // Get card ID from data attribute
    displayCard(cardId, cardContainer); // Call display function with the card ID and the respective container
  });

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

    const cardWidth = 100;
    const cardHeight = 140;
    const svgUrl = "https://assets.codepen.io/67732/card-faces.svg";

    container.innerHTML = ""; // Clear previous content
    const div = document.createElement("div");
    div.classList.add("card");
    div.style.backgroundImage = `url('${svgUrl}')`;
    div.style.backgroundSize = `${cardWidth * ranks.length}px ${
      cardHeight * suits.length
    }px`;

    const [rank, suit] = parseCardId(cardId);
    const suitIndex = suits.indexOf(suit);
    const rankIndex = ranks.indexOf(rank);

    const posX = rankIndex * cardWidth;
    const posY = suitIndex * cardHeight;
    div.style.backgroundPosition = `-${posX}px -${posY + cardHeight}px`;

    container.appendChild(div);
  }

  function parseCardId(cardId) {
    const parts = cardId.split(" of ");
    return [parts[0], parts[1]];
  }
});
