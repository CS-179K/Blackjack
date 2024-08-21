document.addEventListener("DOMContentLoaded", function () {
  const cardContainer = document.getElementById("card");
  const cardId = cardContainer.dataset.cardId; // Get card ID from data attribute

  displayCard(cardId); // Call display function immediately with the provided card ID
  console.log(cardId);
  function displayCard(cardId) {
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

    cardContainer.innerHTML = ""; // Clear previous content
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

    cardContainer.appendChild(div);
  }

  function parseCardId(cardId) {
    const parts = cardId.split(" of ");
    return [parts[0], parts[1]];
  }
});
