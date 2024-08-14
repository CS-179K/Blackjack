from flask import session, render_template, redirect, url_for, Blueprint
import random

game = Blueprint('game', __name__)

card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

def create_deck(num_decks=1):
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [f'{rank} of {suit}' for suit in suits for rank in ranks]
    return deck * num_decks

def shuffle_deck(deck):
    random.shuffle(deck)
    session['deck'] = deck

def deal_card():
    deck = session.get('deck', [])
    if not deck:  # If deck is empty, reshuffle or reinitialize
        deck = shuffle_deck(create_deck())  # Reinitialize and shuffle the deck
    card = deck.pop() if deck else 'No more cards'  # Should not reach this if deck is always replenished
    session['deck'] = deck
    return card

def hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        rank = card.split()[0]
        value += card_values[rank]
        if rank == 'A':
            aces += 1
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def evaluate_winner(player_score, dealer_score):
    if player_score > 21:
        return 'Player busts'
    elif dealer_score > 21:
        return 'Dealer busts Player wins!'
    elif player_score > dealer_score:
        return 'Player wins'
    elif dealer_score > player_score:
        return 'Dealer wins'
    elif player_score == 21:
        return 'Player wins'
    elif dealer_score == 21:
        return 'Dealer wins'
    else:
        return 'Push'


@game.route('/start-game')
def start_game():
    deck = create_deck()
    shuffle_deck(deck)
    session['player_hand'] = [deal_card(), deal_card()]
    session['dealer_hand'] = [deal_card(), deal_card()]
    session['show_dealer_first_card'] = False
    return redirect(url_for('game.show_game'))

@game.route('/')
def show_game():
    player_hand = session.get('player_hand', [])
    dealer_hand = session.get('dealer_hand', [])
    show_dealer_first_card = session.get('show_dealer_first_card', False)
    return render_template('game.html', player_hand=player_hand, dealer_hand=dealer_hand, show_dealer_first_card=show_dealer_first_card)


@game.route('/hit')
def hit():
    player_hand = session.get('player_hand', [])
    player_hand.append(deal_card())
    session['player_hand'] = player_hand
    return redirect(url_for('game.show_game'))

@game.route('/stay')
def stay():
    session['show_dealer_first_card'] = True
    return redirect(url_for('game.evaluate_game'))


@game.route('/evaluate_game')
def evaluate_game():
    dealer_hand = session.get('dealer_hand', [])
    player_hand = session.get('player_hand', [])
    
    while hand_value(dealer_hand) < 17:
        dealer_hand.append(deal_card())
    session['dealer_hand'] = dealer_hand

    player_score = hand_value(player_hand)
    dealer_score = hand_value(dealer_hand)
    result = evaluate_winner(player_score, dealer_score)

    return render_template('game.html', player_hand=player_hand, dealer_hand=dealer_hand,show_dealer_first_card=True, result=result)
