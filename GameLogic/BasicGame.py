import random
import os

# Define card values
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# Create a standard deck of 52 cards
def create_deck(num_decks=1):
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = list(card_values.keys())
    deck = [f'{rank} of {suit}' for suit in suits for rank in ranks]
    return deck * num_decks

# Shuffle the deck
def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

# Deal a card from the deck
def deal_card(deck):
    return deck.pop()

# Calculate the value of the hand
def hand_value(hand):
    value = 0
    ace_count = 0
    for card in hand:
        rank = card.split()[0]
        value += card_values[rank]
        if rank == 'A':
            ace_count += 1
    while value > 21 and ace_count:
        value -= 10
        ace_count -= 1
    return value

# Convert Cards to Strings
def card_to_str(card):
    rank, suit = card.split(' of ')
    suit_symbols = {
        'Hearts': '♥',
        'Diamonds': '♦',
        'Clubs': '♣',
        'Spades': '♠'
    }
    return f"{rank:<2}{suit_symbols[suit]}"

# Print cards in hand
def print_hand(player, hand, hide_first_card=False):
    rows = ['', '', '', '', '']
    card_strs = []

    if hide_first_card:
        rows[0] += "+------+"  
        rows[1] += f"|{card_to_str(hand[0])}   |"  
        rows[2] += "|      |"  
        rows[3] += "|      |"  
        rows[4] += "+------+"  
        rows[0] += "+------+"  
        rows[1] += "|Hidden| "  
        rows[2] += "|      |"  
        rows[3] += "|      |"  
        rows[4] += "+------+"  
        card_strs = [card_to_str(hand[0])]
    else:
        for card in hand:
            card_str = card_to_str(card)
            card_strs.append(card_str)
            rows[0] += "+------+"  
            rows[1] += f"|{card_str}   |"  
            rows[2] += "|      |"  
            rows[3] += "|      |"
            rows[4] += "+------+"  
    
    print(f"\n{player}'s hand:")
    print("\n".join(rows))
    
    if not hide_first_card:
        print(f"{player}'s hand: {', '.join(card_strs)} (Value: {hand_value(hand)})")

# Check for Blackjack
def is_blackjack(hand):
    return hand_value(hand) == 21 and len(hand) == 2

# Simulates the Dealer hitting until 17 or higher
def dealer_turn(deck, hand):
    while hand_value(hand) < 17:
        hand.append(deal_card(deck))
    return hand

# Handles player's actions (Hit, Stand, Double) for a specific hand
def player_turn(deck, hand, hand_number):
    while True:
        action = input(f"Hand {hand_number}: Do you want to 'hit', 'stand', or 'double'? ").strip().lower()
        if action == 'hit':
            hand.append(deal_card(deck))
            print_hand(f'Player Hand {hand_number}', hand)
            if hand_value(hand) > 21:
                print(f"Hand {hand_number} busts!")
                return 'bust'
        elif action == 'stand':
            return 'stand'
        elif action == 'double':
            if len(hand) == 2:
                hand.append(deal_card(deck))
                print_hand(f'Player Hand {hand_number}', hand)
                return 'bust' if hand_value(hand) > 21 else 'stand'
            else:
                print("Double down is only allowed on the initial hand.")
        else:
            print("Invalid action. Please choose 'hit', 'stand', or 'double'.")

# Handles splitting hands based on player choice
def handle_split(deck, hand):
    if len(hand) == 2:
        card1_rank = hand[0].split()[0]
        card2_rank = hand[1].split()[0]
        
        if card1_rank == card2_rank or (card_values[card1_rank] == 10 and card_values[card2_rank] == 10):
            while True:
                split_decision = input("Do you want to split? Type 'yes' or 'no': ").strip().lower()
                if split_decision == 'yes':
                    hand1 = [hand.pop(0), deal_card(deck)]
                    hand2 = [hand.pop(0), deal_card(deck)]
                    print("\nSplitting hands:")
                    print_hand('Player Hand 1', hand1)
                    print_hand('Player Hand 2', hand2)
                    
                    # Play both hands
                    results1 = player_turn(deck, hand1, 1)
                    results2 = player_turn(deck, hand2, 2)
                    return [hand1, hand2], results1, results2
                elif split_decision == 'no':
                    return [hand], 'continue', 'continue'
                else:
                    print("Invalid choice. Please choose 'yes' or 'no'.")
        else:
            return [hand], 'continue', 'continue'
    else:
        return [hand], 'continue', 'continue'

# Determine the winner between the player and dealer hands
def determine_winner(dealer_hand, player_hands):
    dealer_value = hand_value(dealer_hand)
    results = []

    for hand in player_hands:
        player_value = hand_value(hand)
        if player_value > 21:
            results.append("bust")
        elif dealer_value > 21 or player_value > dealer_value:
            results.append("win")
        elif player_value < dealer_value:
            results.append("lose")
        else:
            results.append("push")

    return results

# Check if the deck needs reshuffling
def is_reshuffle_needed(deck):
    return len(deck) < 20

# Clear the console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Main game function
def play_blackjack():
    deck = shuffle_deck(create_deck())

    while True:
        clear_console()
        
        if is_reshuffle_needed(deck):
            print("Deck is being refreshed.")
            deck = shuffle_deck(create_deck())  # Reinitialize deck with a fresh set of cards
        
        player_hand = [deal_card(deck), deal_card(deck)]
        dealer_hand = [deal_card(deck), deal_card(deck)]

        print_hand('Dealer', dealer_hand, hide_first_card=True)
        print_hand('Player', player_hand)

        # Player's turn with possible split
        hands, result1, result2 = handle_split(deck, player_hand)
        hand_statuses = [result1, result2] if len(hands) == 2 else [result1]

        # Execute player actions for all hands that are still active
        for i, hand in enumerate(hands):
            if hand_statuses[i] not in ('bust', 'stand'):
                hand_statuses[i] = player_turn(deck, hand, i + 1)

        # Dealer's turn if no player hands bust
        if all(status != 'bust' for status in hand_statuses):
            dealer_hand = dealer_turn(deck, dealer_hand)
            print_hand('Dealer', dealer_hand)

        # Determine the outcome
        results = determine_winner(dealer_hand, hands)
        for i, hand in enumerate(hands):
            if hand_statuses[i] == 'bust':
                print(f"Hand {i + 1} busts! Dealer wins.")
            elif results[i] == "win":
                print(f"Hand {i + 1} wins!")
            elif results[i] == "lose":
                print(f"Hand {i + 1} loses.")
            elif results[i] == "push":
                print(f"Hand {i + 1} is a push.")

        # Prompt to play again
        play_again = input("Do you want to play again? Type 'yes' or 'no': ").strip().lower()
        if play_again != 'yes':
            break

if __name__ == "__main__":
    play_blackjack()
