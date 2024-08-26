from flask import session, render_template, redirect, url_for, Blueprint, request
from urllib.parse import unquote
import random

cardcount = Blueprint('cardcount', __name__)

card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# Card values and Hi-Lo values
hi_lo_values = {
    '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
    '7': 0, '8': 0, '9': 0,
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

def create_deck(num_decks=1):
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [f'{rank} of {suit}' for suit in suits for rank in ranks]
    return deck * num_decks

def shuffle_deck(deck):
    random.shuffle(deck)
    return deck

def deal_card():
    deck = session.get('deck', [])
    if not deck:
        deck = shuffle_deck(create_deck())
    card = deck.pop() if deck else None
    session['deck'] = deck

    # Update the card count when a card is dealt
    update_card_count(card)

    return card

def hand_value(hand):
    value, ace_count = 0, 0
    for card in hand:
        rank = card.split()[0]
        value += card_values.get(rank, 0)
        if rank == 'A':
            ace_count += 1
    while value > 21 and ace_count:
        value -= 10
        ace_count -= 1
    return value

def initialize_game(shuffle_deck_flag=True):
    if shuffle_deck_flag:
        session['deck'] = shuffle_deck(create_deck())
    else:
        if 'deck' not in session:
            session['deck'] = create_deck()

    session['current_card_count'] = 0

    session['player_hands'] = [[deal_card(), deal_card()]]
    session['dealer_hand'] = [deal_card(), deal_card()]
    session['game_over'] = False
    session['current_hand'] = 0
    session['splitted'] = False
    session['insurance'] = None
    session['show_dealer_hand'] = False
    session['show_new_hand_button'] = False
    session['show_new_game_button'] = False
    session['insurance_prompted'] = False
    session['dealer_blackjack'] = False
    session['doubled_down'] = False
    session['original_bet_before_doubling'] = session.get('bet', 0)

def update_card_count(card):
    rank = card.split()[0]
    card_count_value = hi_lo_values.get(rank, 0)
    current_card_count = session.get('current_card_count', 0) + card_count_value
    session['current_card_count'] = current_card_count


def dealer_turn():
    if session.get('game_over', False) or session.get('show_dealer_hand', False):
        return

    dealer_hand = session.get('dealer_hand', [])
    dealer_score = hand_value(dealer_hand)

    while dealer_score < 17:
        dealer_hand.append(deal_card())
        dealer_score = hand_value(dealer_hand)

    session['show_dealer_hand'] = True
    session['game_over'] = True
    session['show_new_hand_button'] = True
    session['show_new_game_button'] = True

def handle_player_action(action):
    if session.get('game_over', False):
        return redirect(url_for('cardcount.show_game'))

    player_hands = session.get('player_hands', [])
    current_hand_index = session.get('current_hand', 0)
    hand = player_hands[current_hand_index]
    original_bet = session.get('bet', 0)
    doubled_down = session.get('doubled_down', False)
    original_bet_before_doubling = session.get('original_bet_before_doubling', original_bet)

    def update_game_state(is_game_over, result_message=None):
        session['game_over'] = is_game_over
        session['show_new_hand_button'] = is_game_over
        session['show_new_game_button'] = is_game_over
        if result_message:
            session['result'] = result_message

    def handle_bust():
        bet = session.get('bet', 0)
        doubled_down = session.get('doubled_down', False)
        original_bet_before_doubling = session.get('original_bet_before_doubling', bet)

        if doubled_down:
            session['bankroll'] -= (original_bet_before_doubling * 2)
        else:
            session['bankroll'] -= bet

        if not any(hand_value(h) <= 21 for h in session.get('player_hands', [])):
            update_game_state(True, 'You bust!')
            session['show_dealer_hand'] = True

        session['bet'] = original_bet_before_doubling
        session['doubled_down'] = False

        return redirect(url_for('cardcount.show_game'))

    def handle_surrender():
        if doubled_down:
            session['bankroll'] += original_bet_before_doubling
            session['doubled_down'] = False
        else:
            session['bankroll'] -= session.get('bet', 0) / 2

        player_hands.pop(current_hand_index)
        if not player_hands:
            update_game_state(True, 'Player surrenders. You lose half your bet.')
        else:
            if current_hand_index >= len(player_hands):
                session['current_hand'] = len(player_hands) - 1
        session['player_hands'] = player_hands
        return redirect(url_for('cardcount.show_game'))

    def resolve_hand():
        dealer_hand = session.get('dealer_hand', [])
        dealer_hand_value = hand_value(dealer_hand)
        bet = session.get('bet', 0)
        insurance = session.get('insurance', False)
        dealer_blackjack = session.get('dealer_blackjack', False)
        doubled_down = session.get('doubled_down', False)
        original_bet_before_doubling = session.get('original_bet_before_doubling', bet)

        def handle_dealer_blackjack():
            if insurance:
                session['bankroll'] += bet
                update_game_state(True, 'Dealer has Blackjack. Insurance pays 2:1.')
            else:
                session['bankroll'] -= bet
                update_game_state(True, 'Dealer has Blackjack. You lose your bet.')
            return redirect(url_for('cardcount.show_game'))

        if dealer_blackjack:
            return handle_dealer_blackjack()

        if all(hand_value(h) > 21 for h in session.get('player_hands', [])):
            return handle_bust()

        for hand in session.get('player_hands', []):
            player_hand_value = hand_value(hand)
            if player_hand_value > 21:
                continue

            if dealer_hand_value > 21 or player_hand_value > dealer_hand_value:
                if player_hand_value == 21:
                    if doubled_down:
                        session['bankroll'] += original_bet_before_doubling * 3
                        update_game_state(True, 'Blackjack! You won double down.')
                    else:
                        session['bankroll'] += original_bet_before_doubling * 1.5
                        update_game_state(True, 'Blackjack! You win with a 3 to 2 payout.')
                else:
                    if doubled_down:
                        session['bankroll'] += original_bet_before_doubling * 2
                        update_game_state(True, 'You win! You won double down.')
                    else:
                        session['bankroll'] += bet
                        update_game_state(True, 'You win!')
            elif player_hand_value == dealer_hand_value:
                update_game_state(True, 'Push! It\'s a tie.')
            else:
                if doubled_down:
                    session['bankroll'] -= original_bet_before_doubling * 2
                    update_game_state(True, 'Dealer wins. You lost the double down.')
                else:
                    session['bankroll'] -= bet
                    update_game_state(True, 'Dealer wins.')

        session['bet'] = original_bet_before_doubling
        session['doubled_down'] = False

        return redirect(url_for('cardcount.show_game'))

    def is_pair(card1, card2):
        return hand_value([card1]) == hand_value([card2])

    if action == 'hit':
        if hand_value(hand) <= 21:
            hand.append(deal_card())
            session['player_hands'] = player_hands
            if hand_value(hand) > 21:
                return handle_bust()

    elif action == 'stay':
        session['current_hand'] += 1

        if session['current_hand'] >= len(player_hands):
            print("dealer tunr")
            dealer_turn()
            return resolve_hand() 
        else:
            print("end game")
            return redirect(url_for('cardcount.show_game'))

    elif action == 'split':
        if len(hand) == 2 and is_pair(hand[0], hand[1]):
            card1, card2 = hand.pop(0), hand.pop(0)
            new_hand1 = [card1, deal_card()]
            new_hand2 = [card2, deal_card()]
            player_hands[current_hand_index] = new_hand1
            player_hands.append(new_hand2)
            session['player_hands'] = player_hands
            session['splitted'] = True
            session['current_hand'] = len(player_hands) - 2
        return redirect(url_for('cardcount.show_game'))

    elif action == 'double_down':
        if len(hand) == 2:
            card = deal_card()
            hand.append(card)
            if current_hand_index == len(player_hands) - 1:
                session['doubled_down'] = True
                if hand_value(hand) > 21:
                    return handle_bust()
                else:
                    session['player_hands'] = player_hands
                    session['current_hand'] += 1
                    if session['current_hand'] >= len(player_hands):
                        dealer_turn()
                        return resolve_hand()
            else:
                session['current_hand'] = current_hand_index + 1
                session['original_bet_before_doubling'] = session.get('bet', 0)
                session['bet'] *= 2
                session['doubled_down'] = True
                if hand_value(hand) > 21:
                    return handle_bust()
                else:
                    session['player_hands'] = player_hands
                    session['current_hand'] += 1
                    if session['current_hand'] >= len(player_hands):
                        dealer_turn()
                        return resolve_hand()
        return redirect(url_for('cardcount.show_game'))

    elif action == 'surrender':
        return handle_surrender()

    return redirect(url_for('cardcount.show_game'))

@cardcount.route('/player_action/<action>')
def player_action(action):
    print(f"Action received: {action}")
    
    # Handle player action 
    handle_player_action(action)
    
    return redirect(url_for('cardcount.show_game'))

@cardcount.route('/start_game', methods=['POST'])
def start_game():
    if 'bankroll' not in session:
        session['bankroll'] = 1000

    bet = int(request.form.get('bet', 0))
    if bet <= 0 or bet > session['bankroll']:
        return "Invalid bet amount or insufficient bankroll.", 400

    session['bet'] = bet
    initialize_game()

    return redirect(url_for('cardcount.show_game'))

@cardcount.route('/start_new_hand', methods=['POST'])
def start_new_hand():
    if not session.get('game_over', False):
        return redirect(url_for('cardcount.show_game'))

    initialize_game(shuffle_deck_flag=False)
    
    session['show_new_hand_button'] = False
    session['show_new_game_button'] = False
    session['show_dealer_hand'] = False
    session['user_count_result'] = None  
    session['user_count_correct'] = None  

    return redirect(url_for('cardcount.show_game'))


@cardcount.route('/start_new_game', methods=['POST'])
def start_new_game():
    session['bankroll'] = 1000
    initialize_game()
    session['result'] = None
    session['show_new_game_button'] = False
    session['show_new_hand_button'] = False
    
    return redirect(url_for('cardcount.show_game'))

@cardcount.route('/')
def show_game():
    if 'bankroll' not in session:
        session['bankroll'] = 1000

    if 'player_hands' not in session or 'dealer_hand' not in session:
        initialize_game()

    player_hands = session.get('player_hands', [])
    dealer_hand = session.get('dealer_hand', [])
    show_dealer_hand = session.get('show_dealer_hand', False)
    result = session.get('result', None)
    insurance = session.get('insurance', None)
    game_over = session.get('game_over', False)
    splitted = session.get('splitted', False)
    show_new_hand_button = session.get('show_new_hand_button', False)
    bet = session.get('bet', 0)
    show_new_game_button = session.get('show_new_game_button', False)
    insurance_prompted = session.get('insurance_prompted', False)

    player_hand_values = [hand_value(hand) for hand in player_hands]
    player_hands_with_values = list(zip(player_hands, player_hand_values))

    dealer_hand_value = hand_value(dealer_hand) if show_dealer_hand else None

    return render_template('cardcount.html',
                           player_hands_with_values=player_hands_with_values,
                           dealer_hand=dealer_hand,
                           dealer_hand_value=dealer_hand_value,
                           result=result,
                           insurance=insurance,
                           game_over=game_over,
                           splitted=splitted,
                           show_new_hand_button=show_new_hand_button,
                           show_new_game_button=show_new_game_button,
                           show_dealer_hand=show_dealer_hand,
                           bet=bet,
                           bankroll=session['bankroll'])

@cardcount.route('/insurance', methods=['POST'])
def insurance():
    if session.get('game_over', False):
        return redirect(url_for('cardcount.show_game'))

    dealer_hand = session.get('dealer_hand', [])
    dealer_face_up_card = dealer_hand[0] 
    dealer_face_up_is_ace = False
    if dealer_face_up_card and dealer_face_up_card.startswith('A'):
        dealer_face_up_is_ace = True

    if dealer_face_up_is_ace != True:
        return redirect(url_for('cardcount.show_game'))

    insurance_choice = request.form.get('insurance_choice')
    bet = session.get('bet', 0)

    if insurance_choice == 'take':
        session['insurance'] = True
        session['bankroll'] -= bet / 2
    else:
        session['insurance'] = False

    dealer_hand_value = hand_value(dealer_hand)
    
    if dealer_face_up_is_ace and dealer_hand_value == 21:
        session['dealer_blackjack'] = True
    else:
        session['dealer_blackjack'] = False

    return redirect(url_for('cardcount.show_game'))

@cardcount.route('/check_card_count', methods=['POST'])
def check_card_count():
    user_count = int(request.form.get('user_count', 0))
    correct_count = session.get('current_card_count', 0)

    if user_count == correct_count:
        session['user_count_correct'] = True
        session['user_count_result'] = f"Correct! The count is {correct_count}."
        # Console Debug
        print(f"User's guess: {user_count}. Correct! The actual count is {correct_count}.")
    else:
        session['user_count_correct'] = False
        session['user_count_result'] = f"Incorrect. The count is {correct_count}."
        # Console Debug
        print(f"User's guess: {user_count}. Incorrect. The actual count is {correct_count}.")

    return redirect(url_for('cardcount.show_game'))
